namespace com.gncloud.HyperV.Agent.Service
{
    using com.gncloud.HyperV.Agent.Script;
    using com.gncloud.HyperV.Agent.Management;

    class HyperVService
    {
        private static string WINDOWS_SERVER_2012_R2 = "winsv2012r2";
        private static string WINDOWS10 = "win10";
        private static string WINDOWS_SERVER_2012_R2_DISK_NAME = "windows_server_2012_r2.vhdx";
        private static string WINDOWS10_DISK_NAME = "windows10.vhdx";
        private static string ORIGINAL_DISK_PATH = "C:\\images";

        private HyperVScript hvctrl;
        private string serverName;

        public HyperVService(string getServerName)
        {
            this.serverName = getServerName;
            this.hvctrl = new HyperVScript();
        }

        public string NewVM(
            string vmName,
            long generation)
        {
            return hvctrl.NewVM(vmName, generation);
        }

        public string SetVM(
            string vmName,
            long processorCount,
            long memoryStartupBytes)
        {
            return hvctrl.SetVM(vmName, processorCount, memoryStartupBytes);
        }

        public string ConvertVHD(
            int id,
            string vmName,
            string osType)
        {
            string diskName;

            if (osType.Equals("winsv2012r2"))
            {
                diskName = WINDOWS_SERVER_2012_R2_DISK_NAME;
            }
            else if (osType.Equals("windows10"))
            {
                diskName = WINDOWS10_DISK_NAME;
            }
            else
            {
                // Default
                diskName = WINDOWS_SERVER_2012_R2_DISK_NAME;
            }

            string original_path = ORIGINAL_DISK_PATH + "\\" + diskName;
            string new_path = ORIGINAL_DISK_PATH + "\\" + id + "_" + vmName + "\\" + diskName;

            return hvctrl.ConvertVHD(original_path, new_path);
        }

        public string AddVMHardDiskDrive(
            int id,
            string vmName,
            string osType)
        {
            string diskName;

            if (osType.Equals("winsv2012r2"))
            {
                diskName = WINDOWS_SERVER_2012_R2_DISK_NAME;
            }
            else if (osType.Equals("windows10"))
            {
                diskName = WINDOWS10_DISK_NAME;
            }
            else
            {
                // Default
                diskName = WINDOWS_SERVER_2012_R2_DISK_NAME;
            }

            string path = ORIGINAL_DISK_PATH + "\\" + id + "_" + vmName + "\\" + diskName;

            return hvctrl.AddVMHardDiskDrive(vmName, path);
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
