namespace com.gncloud.HyperV.Agent.Service
{
    using com.gncloud.HyperV.Agent.Script;
    using com.gncloud.HyperV.Agent.Management;

    class HyperVService
    {
        private string serverName;

        public HyperVService(string getServerName)
        {
            this.serverName = getServerName;
        }

        public void createVM(
            string vmName,
            string generation,
            string processorCount,
            string memoryStartupBytes,
            string path)
        {
            HyperVScript.NewVM(vmName, generation);
            HyperVScript.SetVM(vmName, processorCount, memoryStartupBytes);
            HyperVScript.AddVMHardDiskDrive(vmName, path);
        }

        public void startVM(
            string vmName)
        {
            StartVM.action(this.serverName, vmName);
        }

        public void stopVM(
            string vmName)
        {
            StopVM.action(this.serverName, vmName);
        }

        public void removeVM(
            string vmName)
        {
            RemoveVM.action(this.serverName, vmName);
        }
    }
}
