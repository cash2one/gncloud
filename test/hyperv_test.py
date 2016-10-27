# -*- coding: utf-8 -*-
__author__ = 'jhjeon'

import time
import logging

import wmi

LOG = logging.getLogger('hyperv')

SERVER = "60.196.149.135"
USER = r"administrator"
PASSWORD = "fastcat4321@"
INSTANCE = {
    "name": "test-server",
    "memory_mb": 1024,
    "vcpus": 1,
    "vhdfile": "",
    "int_network": "Default Network",
}

HYPERV_VM_STATE_ENABLED = 2
HYPERV_VM_STATE_DISABLED = 3
HYPERV_VM_STATE_REBOOT = 10
HYPERV_VM_STATE_RESET = 11
HYPERV_VM_STATE_PAUSED = 32768
HYPERV_VM_STATE_SUSPENDED = 32769

WMI_JOB_STATUS_STARTED = 4096
WMI_JOB_STATE_RUNNING = 4
WMI_JOB_STATE_COMPLETED = 7


def _wait_for_job(job_path):
    job_wmi_path = job_path.replace('\\', '/')
    job = wmi.WMI(moniker=job_wmi_path)

    while job.JobState == WMI_JOB_STATE_RUNNING:
        time.sleep(1.)
        job = wmi.WMI(moniker=job_wmi_path)
    LOG.debug("Job %s FINISHED; %s; %s" % (job_path, job.JobStatus, job.GetError()))
    return job


class Instance(object):
    def __init__(self, hyperv, name, vhdfile=None, memory_mb=1024, vcpus=1, int_network=None):
        LOG.debug('Instance > init')
        self.hyperv = hyperv
        self.conn = self.hyperv.conn
        self.name = name
        self.vhdfile = vhdfile
        self.memory_mb = memory_mb
        self.vcpus = vcpus
        self.int_network = int_network

    # 인스턴스 작성 및 인스턴스 초기 설정
    def create(self):
        self._create(self.name)
        self.set_memory(self.memory_mb)
        self.set_cpus(self.vcpus)

        # if self.vhdfile:
        #    self.add_vhd(self.vhdfile)
        #
        # if self.int_network:
        #     self.create_nic(self.int_network)

    # VM 인스턴스 생성
    def _create(self, name):
        data = self.conn.Msvm_VirtualSystemSettingData.new()
        data.ElementName = name

        self.hyperv.management.DefineSystem(
            ResourceSettings=[],
            ReferenceConfiguration=None,
            SystemSettings=data.GetText_(1)
        )
        self.vm = self.conn.Msvm_ComputerSystem(ElementName=name)[0]
        # get settings
        self.vm_settings = self.vm.associators(
            wmi_result_class='Msvm_VirtualSystemSettingData')
        self.vm_setting = self.vm_settings[0]
        self.mem_setting = self.vm_setting.associators(
            wmi_result_class='Msvm_MemorySettingData')[0]
        self.cpu_settings = self.vm_setting.associators(
            wmi_result_class='Msvm_ProcessorSettingData')[0]
        self.rasds = self.vm_settings[0].associators(
            wmi_result_class='MSVM_ResourceAllocationSettingData')
        LOG.info('Created vm %s...', name)

    # 메모리 설정
    def set_memory(self, memory_mb):
        mem = long(str(memory_mb))
        self.mem_setting.VirtualQuantity = mem
        self.mem_setting.Reservation = mem
        self.mem_setting.Limit = mem
        self.hyperv.management.ModifyResourceSettings(ResourceSettings=[self.mem_setting.GetText_(1)])
        LOG.info('Set memory [%s MB] for vm %s...', mem, self.name)

    # CPU 설정
    def set_cpus(self, vcpus):
        vcpus = long(vcpus)
        self.cpu_settings.VirtualQuantity = vcpus
        self.cpu_settings.Reservation = vcpus
        self.cpu_settings.Limit = 100000 # static assignment to 100%
        self.hyperv.management.ModifyResourceSettings(ResourceSettings=[self.cpu_settings.GetText_(1)])
        LOG.info('Set vcpus [%s] for vm %s...', vcpus, self.name)

    def start(self):
        job, ret_val = self.vm.RequestStateChange(HYPERV_VM_STATE_ENABLED)
        if ret_val == WMI_JOB_STATUS_STARTED:
            _wait_for_job(job)
        LOG.info("Booting %s ", self.name)

    def stop(self):
        LOG.info("Stopping %s ...", self.name)
        job, ret_val = self.vm.RequestStateChange(HYPERV_VM_STATE_DISABLED)
        if ret_val == WMI_JOB_STATUS_STARTED:
            _wait_for_job(job)
        LOG.info("Stopped %s ", self.name)

    def destroy(self):
        self.stop()
        job, ret_code = self.hyperv.management.DestroySystem(self.vm.path_())
        if ret_code == WMI_JOB_STATUS_STARTED:
            _wait_for_job(job)


class HyperV(object):
    def __init__(self, server_name, user, passwd):
        LOG.debug('HyperV > init')
        connection = wmi.connect_server(server=server_name, user=user, password=passwd, namespace=r"root\virtualization\v2")
        self.conn = wmi.WMI(wmi=connection)
        self.management = self.conn.Msvm_VirtualSystemManagementService()[0]

    def create(self, *args, **kwargs):
        LOG.debug('HyperV > create')
        LOG.info('다음 옵션으로 가상OS 생성: %s' % kwargs)
        vm = Instance(self, *args, **kwargs)
        vm.create()
        return vm


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    INSTANCE['name'] = "test-sv"
    INSTANCE['memory_mb'] = 512
    INSTANCE['vcpus'] = 1

    hyperv = HyperV(SERVER, USER, PASSWORD)
    instance = hyperv.create(**INSTANCE)

    instance.start()
