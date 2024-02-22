# -*- mode: ruby -*-
# vi: set ft=ruby :

configuration = ENV['CONFIG']

Vagrant.configure('2') do |config|
  config.vagrant.plugins = 'vagrant-libvirt'

  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.ssh.disable_deprecated_algorithms = true
  config.vm.boot_timeout = 3600

  config.vm.provider 'libvirt' do |v|
    v.uri = 'qemu:///system'
    v.memory = 4096
    v.machine_type = 'q35'
    v.cpu_mode = 'host-passthrough'
    v.cpus = 2
    v.disk_bus = 'scsi'
    v.disk_driver cache: 'writeback', discard: 'unmap'
    v.random_hostname = true
  end

  target_distros = {
    almalinux: 'almalinux/8',
    # centosstream: 'generic/centos8s',
    eurolinux: 'eurolinux-vagrant/eurolinux-8',
    rocky: 'generic/rocky8'
  }

  target_distros.each_pair do |vm, box|
    config.vm.define "#{vm}_9" do |machine|
      machine.vm.box = "#{box}"
      machine.vm.hostname = "#{vm}-9.test"

      if [vm, box] == target_distros.to_a.last
        machine.vm.provision 'ansible' do |ansible|
          ansible.compatibility_mode = '2.0'
          ansible.limit = 'all'
          ansible.playbook = "ci/ansible/#{configuration}.yaml"
          ansible.config_file = 'ci/ansible/ansible.cfg'
        end
      end
    end
  end
end
