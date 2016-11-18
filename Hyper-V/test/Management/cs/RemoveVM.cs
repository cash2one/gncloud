

namespace com.gncloud.HyperV.Agent.Management
{
    using System;
    using System.Globalization;
    using System.Management;

    static class RemoveVM
    {
        internal static void
        action(
            string serverName,
            string vmName)
        {
            ManagementScope scope = new ManagementScope(@"\\" + serverName + @"\root\virtualization\v2", null);

            using (ManagementObject vm = WmiUtilities.GetVirtualMachine(vmName, scope))
            using (ManagementObject managementService = WmiUtilities.GetVirtualMachineManagementService(scope))
            using (ManagementBaseObject inParams = managementService.GetMethodParameters("DestroySystem"))
            {
                inParams["AffectedSystem"] = vm.Path;

                Console.WriteLine("Removing Virtual Machine \"{0}\" ({1})...",
                        vm["ElementName"], vm["Name"]);

                using (ManagementBaseObject outParams =
                    managementService.InvokeMethod("DestroySystem", inParams, null))
                {
                    WmiUtilities.ValidateOutput(outParams, scope);
                }
            }
        }
    }
}