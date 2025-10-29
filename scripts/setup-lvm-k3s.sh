#!/bin/bash

# ============================================================================
# Script de Configuração LVM para K3s + Rancher + LLM Workloads
# ============================================================================
# Servidor: Ubuntu 24.04 com NVIDIA RTX PRO 6000 Blackwell
# Autor: GitHub Copilot
# Data: 28 de Outubro de 2025
# ============================================================================

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funções auxiliares
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script deve ser executado como root"
        exit 1
    fi
}

verify_vg_space() {
    local free_space=$(vgs ubuntu-vg --noheadings -o vg_free --units g | tr -d ' ' | sed 's/g//')
    local required=3500  # ~3.5 TB
    
    if (( $(echo "$free_space < $required" | bc -l) )); then
        log_error "Espaço insuficiente no VG. Necessário: ${required}G, Disponível: ${free_space}G"
        exit 1
    fi
    
    log_info "Espaço disponível: ${free_space}G"
}

# ============================================================================
# FASE 1: Verificação de Pré-requisitos
# ============================================================================
check_prerequisites() {
    log_info "=== Verificando pré-requisitos ==="
    
    check_root
    
    # Verificar se LVM está disponível
    if ! command -v lvcreate &> /dev/null; then
        log_error "LVM não está instalado"
        exit 1
    fi
    
    # Verificar Volume Group
    if ! vgs ubuntu-vg &> /dev/null; then
        log_error "Volume Group 'ubuntu-vg' não encontrado"
        exit 1
    fi
    
    verify_vg_space
    
    # Verificar se K3s já está instalado
    if command -v k3s &> /dev/null; then
        log_warn "K3s já está instalado. Este script deve ser executado ANTES da instalação do K3s."
        read -p "Continuar mesmo assim? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_info "✓ Pré-requisitos verificados"
}

# ============================================================================
# FASE 2: Criar Diretórios
# ============================================================================
create_directories() {
    log_info "=== Criando estrutura de diretórios ==="
    
    mkdir -p /var/lib/rancher/k3s-containerd
    mkdir -p /var/lib/rancher/k3s-storage
    mkdir -p /data/{llm-models,rancher,registry,scratch}
    mkdir -p /var/log/kubernetes
    
    log_info "✓ Diretórios criados"
}

# ============================================================================
# FASE 3: Criar Logical Volumes
# ============================================================================
create_logical_volumes() {
    log_info "=== Criando Logical Volumes ==="
    
    # Array de volumes: nome, tamanho, label
    declare -a volumes=(
        "containerd-lv:300G:k3s-containerd"
        "k3s-storage-lv:1.5T:k3s-storage"
        "llm-models-lv:1T:llm-models"
        "rancher-data-lv:200G:rancher-data"
        "logs-lv:100G:k8s-logs"
        "registry-lv:300G:container-registry"
        "scratch-lv:200G:scratch"
    )
    
    for volume in "${volumes[@]}"; do
        IFS=':' read -r lv_name size label <<< "$volume"
        
        log_info "Criando $lv_name ($size)..."
        
        if lvs ubuntu-vg/$lv_name &> /dev/null; then
            log_warn "LV $lv_name já existe, pulando..."
            continue
        fi
        
        lvcreate -L $size -n $lv_name ubuntu-vg
        mkfs.ext4 -L $label /dev/ubuntu-vg/$lv_name
        
        log_info "✓ $lv_name criado e formatado"
    done
    
    log_info "✓ Todos os volumes criados"
}

# ============================================================================
# FASE 4: Configurar /etc/fstab
# ============================================================================
configure_fstab() {
    log_info "=== Configurando /etc/fstab ==="
    
    # Backup do fstab original
    cp /etc/fstab /etc/fstab.backup-$(date +%Y%m%d-%H%M%S)
    
    # Adicionar entradas
    cat >> /etc/fstab << 'EOF'

# Volumes LVM para K3s + Rancher + LLM Workloads - Adicionado em $(date)
/dev/ubuntu-vg/containerd-lv    /var/lib/rancher/k3s-containerd    ext4    defaults,noatime    0    2
/dev/ubuntu-vg/k3s-storage-lv   /var/lib/rancher/k3s-storage       ext4    defaults,noatime    0    2
/dev/ubuntu-vg/llm-models-lv    /data/llm-models                   ext4    defaults,noatime    0    2
/dev/ubuntu-vg/rancher-data-lv  /data/rancher                      ext4    defaults,noatime    0    2
/dev/ubuntu-vg/logs-lv          /var/log/kubernetes                ext4    defaults,noatime    0    2
/dev/ubuntu-vg/registry-lv      /data/registry                     ext4    defaults,noatime    0    2
/dev/ubuntu-vg/scratch-lv       /data/scratch                      ext4    defaults,noatime    0    2
EOF
    
    log_info "✓ /etc/fstab configurado"
}

# ============================================================================
# FASE 5: Montar Volumes
# ============================================================================
mount_volumes() {
    log_info "=== Montando volumes ==="
    
    if mount -a; then
        log_info "✓ Todos os volumes montados com sucesso"
    else
        log_error "Erro ao montar volumes. Verifique /etc/fstab"
        exit 1
    fi
    
    # Verificar montagens
    df -h | grep -E "(containerd|k3s-storage|llm-models|rancher|registry|scratch|logs)"
}

# ============================================================================
# FASE 6: Otimizações
# ============================================================================
apply_optimizations() {
    log_info "=== Aplicando otimizações ==="
    
    # Otimizações de filesystem para volumes de alto I/O
    tune2fs -o journal_data_writeback /dev/ubuntu-vg/k3s-storage-lv
    tune2fs -o journal_data_writeback /dev/ubuntu-vg/llm-models-lv
    tune2fs -o journal_data_writeback /dev/ubuntu-vg/scratch-lv
    
    # Ajustar permissões
    chown -R root:root /var/lib/rancher
    chmod 755 /var/lib/rancher/k3s-containerd
    chmod 755 /var/lib/rancher/k3s-storage
    
    chown -R root:root /data/{llm-models,rancher,registry}
    chmod 755 /data/{llm-models,rancher,registry,scratch}
    
    log_info "✓ Otimizações aplicadas"
}

# ============================================================================
# FASE 7: Configurar K3s
# ============================================================================
configure_k3s_prerequisites() {
    log_info "=== Configurando pré-requisitos K3s ==="
    
    # Kernel modules
    modprobe br_netfilter
    modprobe overlay
    
    cat > /etc/modules-load.d/k3s.conf << 'EOF'
br_netfilter
overlay
EOF
    
    # Sysctl
    cat > /etc/sysctl.d/k3s.conf << 'EOF'
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF
    
    sysctl --system > /dev/null 2>&1
    
    # Criar diretório de configuração K3s
    mkdir -p /etc/rancher/k3s
    
    # Criar arquivo de configuração K3s
    cat > /etc/rancher/k3s/config.yaml << 'EOF'
# K3s Configuration for LLM Workloads
data-dir: /var/lib/rancher/k3s-containerd
default-local-storage-path: /var/lib/rancher/k3s-storage
kubelet-arg:
  - "eviction-hard=nodefs.available<5%,nodefs.inodesFree<5%,imagefs.available<10%"
  - "eviction-soft=nodefs.available<10%,nodefs.inodesFree<10%,imagefs.available<15%"
  - "eviction-soft-grace-period=nodefs.available=5m,nodefs.inodesFree=5m,imagefs.available=5m"
EOF
    
    log_info "✓ Pré-requisitos K3s configurados"
}

# ============================================================================
# FASE 8: Configurar Scripts de Manutenção
# ============================================================================
configure_maintenance_scripts() {
    log_info "=== Configurando scripts de manutenção ==="
    
    # Script de limpeza de scratch
    cat > /etc/cron.weekly/cleanup-scratch << 'EOF'
#!/bin/bash
# Limpar arquivos em /data/scratch com mais de 7 dias
find /data/scratch -type f -mtime +7 -delete
find /data/scratch -type d -empty -delete
EOF
    chmod +x /etc/cron.weekly/cleanup-scratch
    
    # Logrotate para logs Kubernetes
    cat > /etc/logrotate.d/kubernetes << 'EOF'
/var/log/kubernetes/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
    
    log_info "✓ Scripts de manutenção configurados"
}

# ============================================================================
# FASE 9: Criar Script de Instalação K3s
# ============================================================================
create_k3s_install_script() {
    log_info "=== Criando script de instalação K3s ==="
    
    cat > /root/install-k3s.sh << 'EOF'
#!/bin/bash

echo "=== Instalando K3s ==="

# Instalar K3s com configuração customizada
curl -sfL https://get.k3s.io | sh -

echo "Aguardando K3s iniciar..."
sleep 30

# Configurar kubectl para usuário atual
ACTUAL_USER=$(logname)
USER_HOME=$(eval echo ~$ACTUAL_USER)

mkdir -p $USER_HOME/.kube
cp /etc/rancher/k3s/k3s.yaml $USER_HOME/.kube/config
chown $ACTUAL_USER:$ACTUAL_USER $USER_HOME/.kube/config

echo ""
echo "✓ K3s instalado com sucesso!"
echo ""
echo "Execute como usuário normal:"
echo "  export KUBECONFIG=~/.kube/config"
echo "  kubectl get nodes"
echo ""
echo "Próximo passo: Instalar Rancher"
echo "  kubectl create namespace cattle-system"
echo "  helm repo add rancher-latest https://releases.rancher.com/server-charts/latest"
echo "  helm install rancher rancher-latest/rancher --namespace cattle-system --set hostname=rancher.local --set replicas=1"
EOF
    
    chmod +x /root/install-k3s.sh
    
    log_info "✓ Script de instalação criado em /root/install-k3s.sh"
}

# ============================================================================
# FASE 10: Verificação Final
# ============================================================================
final_verification() {
    log_info "=== Verificação final ==="
    
    echo ""
    echo "==================== STATUS DOS VOLUMES ===================="
    df -h | grep -E "(Filesystem|containerd|k3s-storage|llm-models|rancher|registry|scratch|logs)"
    
    echo ""
    echo "==================== LVM STATUS ===================="
    lvs -o lv_name,vg_name,lv_size,lv_path | grep ubuntu-vg
    
    echo ""
    echo "==================== ESPAÇO LIVRE ===================="
    vgs ubuntu-vg -o vg_name,vg_size,vg_free
    
    echo ""
    log_info "✓ Configuração completa!"
    echo ""
    echo "==================== PRÓXIMOS PASSOS ===================="
    echo ""
    echo "1. Testar reboot:"
    echo "   sudo reboot"
    echo ""
    echo "2. Após reboot, verificar montagens:"
    echo "   df -h"
    echo ""
    echo "3. Instalar K3s:"
    echo "   sudo /root/install-k3s.sh"
    echo ""
    echo "4. Instalar NVIDIA Device Plugin:"
    echo "   kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml"
    echo ""
    echo "5. Baixar modelos LLM em /data/llm-models/"
    echo ""
    echo "==========================================================="
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    echo "============================================================================"
    echo "  Configuração LVM para K3s + Rancher + LLM Workloads"
    echo "  Servidor: NVIDIA RTX PRO 6000 Blackwell"
    echo "============================================================================"
    echo ""
    
    check_prerequisites
    
    read -p "Continuar com a criação dos volumes? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warn "Operação cancelada pelo usuário"
        exit 0
    fi
    
    create_directories
    create_logical_volumes
    configure_fstab
    mount_volumes
    apply_optimizations
    configure_k3s_prerequisites
    configure_maintenance_scripts
    create_k3s_install_script
    final_verification
    
    echo ""
    log_info "✓ Setup completo! Sistema pronto para K3s + LLM workloads."
}

# Executar
main "$@"
