# -*- mode: ruby -*-
# vi: set ft=ruby :

configuration = ENV['CONFIG']

Vagrant.configure('2') do |config|
  config.vagrant.plugins = 'vagrant-libvirt'

  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.vm.box = 'generic/centos7'
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

  target_distros = ['almalinux', 'centosstream', 'eurolinux', 'oraclelinux', 'rocky']

  target_distros.each do |target_distro|
    config.vm.define "#{target_distro}_8" do |machine|
      machine.vm.hostname = "#{target_distro}-8.test"

      if target_distro == target_distros[-1]
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
