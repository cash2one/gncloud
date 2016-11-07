using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace test
{
    using System;
    using System.Globalization;
    using System.Management;
    using Microsoft.Wmi.HyperV.Common;

    static class Generation2VMCreateSample
    {
        /// <summary>
        /// Create a Generation 2 VM.
        /// </summary>
        /// <param name="serverName">The name of the server on which to create the Generation 2 VM.</param>
        /// <param name="vmName">The name of the VM to create.</param>
        public static void
        CreateGeneration2VM(
            string serverName,
            string vmName)
        {
            ManagementPath classPath = new ManagementPath()
            {
                Server = serverName,
                NamespacePath = @"\root\virtualization\v2",
                ClassName = "Msvm_VirtualSystemSettingData"
            };

            using (ManagementClass virtualSystemSettingClass = new ManagementClass(classPath))
            {
                ManagementScope scope = new ManagementScope(@"\\" + serverName + @"\root\virtualization\v2", null);

                virtualSystemSettingClass.Scope = scope;

                using (ManagementObject virtualSystemSetting = virtualSystemSettingClass.CreateInstance())
                {
                    virtualSystemSetting["ElementName"] = vmName;
                    virtualSystemSetting["ConfigurationDataRoot"] = "C:\\ProgramData\\Microsoft\\Windows\\Hyper-V\\";
                    virtualSystemSetting["VirtualSystemSubtype"] = "Microsoft:Hyper-V:SubType:2";

                    string embeddedInstance = virtualSystemSetting.GetText(TextFormat.WmiDtd20);

                    // Get the management service, VM object and its settings.
                    using (ManagementObject service = WmiUtilities.GetVirtualMachineManagementService(scope))
                    using (ManagementBaseObject inParams = service.GetMethodParameters("DefineSystem"))
                    {
                        inParams["SystemSettings"] = embeddedInstance;

                        using (ManagementBaseObject outParams = service.InvokeMethod("DefineSystem", inParams, null))
                        {
                            Console.WriteLine("ret={0}", outParams["ReturnValue"]);
                        }
                    }
                }
            }
        }
    }
}
