#!/bin/bash

INVENTORY_FILE="inventory.ini"
VAULT_FILE="vault.yml"
HOST_PREFIX="mikrotik"

# check ansible-vault
check_vault() {
    if ! command -v ansible-vault &> /dev/null; then
        echo "Error: ansible-vault is not installed!"
        echo "Install it with: pip install ansible"
        exit 1
    fi
}

show_help() {
    echo "Usage: $0 [command] [options]"
    echo "Commands:"
    echo "  add <ip> <user> <pass>   - Add a new host (password will be encrypted)"
    echo "  del <number|ip>          - Delete host by number or IP"
    echo "  show                     - Show all hosts (without passwords)"
    echo "  edit-vault               - Edit encrypted vault file"
    echo "  view-vault               - View encrypted vault file"
    echo "  change-vault-password    - Change vault password"
    echo ""
    echo "Example:"
    echo "  $0 add 192.168.1.1 admin password123"
    echo "  $0 del 1"
    echo "  $0 del 192.168.1.1"
    echo "  $0 show"
    echo ""
    echo "For ansible usage:"
    echo "  ansible allmikrotik -i inventory.ini --ask-vault-pass -m ping"
}

# check inventory fiel
initialize_files() {
    if [ ! -f "$INVENTORY_FILE" ]; then
        cat > "$INVENTORY_FILE" << EOF
[allmikrotik]
# automatic add host

EOF
    fi
    
    # create vault file
    if [ ! -f "$VAULT_FILE" ]; then
        ansible-vault create "$VAULT_FILE" << EOF
# Encrypted passwords for mikrotik hosts
# Format:
# mikrotik1_password: encrypted_password
# mikrotik2_password: encrypted_password

EOF
    fi
}

add_host() {
    if [ $# -ne 3 ]; then
        echo "Error: add command requires 3 arguments: ip user pass"
        echo "Usage: $0 add <ip> <user> <pass>"
        exit 1
    fi
    
    check_vault
    initialize_files
    
    local ip="$1"
    local user="$2"
    local pass="$3"
    
    if grep -q "ansible_host=$ip" "$INVENTORY_FILE"; then
        echo "Error: Host with IP $ip already exists!"
        exit 1
    fi
    
    # find last number host
    local last_num=$(grep -o "${HOST_PREFIX}[0-9]*" "$INVENTORY_FILE" | grep -o "[0-9]*" | sort -n | tail -1)
    if [ -z "$last_num" ]; then
        last_num=0
    fi
    
    local next_num=$((last_num + 1))
    local hostname="${HOST_PREFIX}${next_num}"
    
    # add new host to inventory.ini
    cat >> "$INVENTORY_FILE" << EOF
$hostname ansible_host=$ip ansible_user=$user ansible_connection=ansible.netcommon.network_cli ansible_network_os=community.routeros.routeros ansible_become=yes ansible_become_method=enable

EOF
    
    # save password in vault
    # deceript and encreapt file
    local temp_vault="/tmp/vault_$$.yml"
    
    # read file vault
    ansible-vault view "$VAULT_FILE" > "$temp_vault" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Failed to decrypt vault file. Please check your vault password."
        exit 1
    fi
    
    # add new password
    echo "${hostname}_password: $pass" >> "$temp_vault"
    
    # resave password
    ansible-vault encrypt --output "$VAULT_FILE" "$temp_vault"
    
    rm -f "$temp_vault"
    
    echo "Host $hostname added successfully!"
    echo "IP: $ip"
    echo "User: $user"
    echo "Password: *** (encrypted in vault.yml)"
    echo ""
    echo "To use with ansible, run:"
    echo "ansible allmikrotik -i $INVENTORY_FILE --ask-vault-pass -m ping"
}

show_hosts() {
    initialize_files
    
    echo "=== Mikrotik Inventory ==="
    echo "Password storage: Encrypted in $VAULT_FILE"
    echo ""
    
    local line_num=1
    while IFS= read -r line; do
        if [[ "$line" =~ ^${HOST_PREFIX}[0-9]+ ]]; then
 
            local hostname=$(echo "$line" | awk '{print $1}')
            local ip=$(echo "$line" | grep -o 'ansible_host=[^ ]*' | cut -d= -f2)
            local user=$(echo "$line" | grep -o 'ansible_user=[^ ]*' | cut -d= -f2)
            
            echo "$line_num) $hostname"
            echo "   IP: $ip"
            echo "   User: $user"
            echo "   Password: [ENCRYPTED]"
            echo ""
            ((line_num++))
        fi
    done < "$INVENTORY_FILE"
    
    if [ $line_num -eq 1 ]; then
        echo "No hosts found in inventory."
    fi
    
    echo ""
    echo "To use with ansible:"
    echo "ansible allmikrotik -i $INVENTORY_FILE --ask-vault-pass -m ping"
}


delete_host() {
    if [ $# -ne 1 ]; then
        echo "Error: del command requires 1 argument: number or IP"
        echo "Usage: $0 del <number|ip>"
        exit 1
    fi
    
    check_vault
    initialize_files
    
    local target="$1"
    local hostname=""
    
    # number enter
    if [[ "$target" =~ ^[0-9]+$ ]]; then
        # find host by number
        local line_num=1
        
        while IFS= read -r line; do
            if [[ "$line" =~ ^${HOST_PREFIX}[0-9]+ ]]; then
                if [ $line_num -eq $target ]; then
                    hostname=$(echo "$line" | awk '{print $1}')
                    break
                fi
                ((line_num++))
            fi
        done < "$INVENTORY_FILE"
        
        if [ -z "$hostname" ]; then
            echo "Error: No host found with number $target"
            exit 1
        fi
        
        # remove host selected
        local temp_file="${INVENTORY_FILE}.tmp"
        grep -v "^$hostname " "$INVENTORY_FILE" > "$temp_file"
        mv "$temp_file" "$INVENTORY_FILE"
        
    # find by ip
    else
        hostname=$(grep "ansible_host=$target" "$INVENTORY_FILE" | awk '{print $1}')
        
        if [ -z "$hostname" ]; then
            echo "Error: No host found with IP $target"
            exit 1
        fi
        
        # remove host
        local temp_file="${INVENTORY_FILE}.tmp"
        grep -v "ansible_host=$target" "$INVENTORY_FILE" > "$temp_file"
        mv "$temp_file" "$INVENTORY_FILE"
    fi
    
    local temp_vault="/tmp/vault_$$.yml"
    
    ansible-vault view "$VAULT_FILE" > "$temp_vault" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Failed to decrypt vault file. Host removed from inventory but vault unchanged."
        exit 1
    fi
    
    grep -v "^${hostname}_password:" "$temp_vault" > "${temp_vault}.new"
    
    ansible-vault encrypt --output "$VAULT_FILE" "${temp_vault}.new"
    
    rm -f "$temp_vault" "${temp_vault}.new"
    
    echo "Host $hostname deleted successfully from inventory and vault."
}

view_vault() {
    check_vault
    initialize_files
    
    if [ ! -f "$VAULT_FILE" ]; then
        echo "Vault file does not exist."
        exit 1
    fi
    
    echo "=== Encrypted Vault Contents ==="
    ansible-vault view "$VAULT_FILE"
}

edit_vault() {
    check_vault
    initialize_files
    
    if [ ! -f "$VAULT_FILE" ]; then
        echo "Vault file does not exist."
        exit 1
    fi
    
    ansible-vault edit "$VAULT_FILE"
}

change_vault_password() {
    check_vault
    initialize_files
    
    if [ ! -f "$VAULT_FILE" ]; then
        echo "Vault file does not exist."
        exit 1
    fi
    
    ansible-vault rekey "$VAULT_FILE"
}

case "$1" in
    add)
        shift
        add_host "$@"
        ;;
    del)
        shift
        delete_host "$@"
        ;;
    show)
        show_hosts
        ;;
    view-vault)
        view_vault
        ;;
    edit-vault)
        edit_vault
        ;;
    change-vault-password)
        change_vault_password
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo ""
        show_help
        exit 1
        ;;
esac
