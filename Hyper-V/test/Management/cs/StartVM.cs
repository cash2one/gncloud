
namespace com.gncloud.HyperV.Agent.Management
{
    using System;
    using System.Globalization;
    using System.Management;

    static class StartVM
    {
        internal static void
        action(
            string serverName,
            string vmName)
        {
            ManagementScope scope = new ManagementScope(@"\\" + serverName + @"\root\virtualization\v2", null);

            using (ManagementObject vm = WmiUtilities.GetVirtualMachine(vmName, scope))
            using (ManagementBaseObject inParams = vm.GetMethodParameters("RequestStateChange"))
            {
                inParams["RequestedState"] = 2;

                using (ManagementBaseObject outParams =
                    vm.InvokeMethod("RequestStateChange", inParams, null))
                {
                    WmiUtilities.ValidateOutput(outParams, scope);
                }
            }
        }
    }
}