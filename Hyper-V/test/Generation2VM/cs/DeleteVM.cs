// THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
// ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
// PARTICULAR PURPOSE.
//
// Copyright (c) Microsoft. All rights reserved.

namespace Microsoft.Samples.HyperV.Generation2VM
{
    using System;
    using System.Globalization;
    using System.Management;
    using Microsoft.Samples.HyperV.Common;

    static class Generation2VMDeleteSample
    {
        /// <summary>
        /// Create a Generation 2 VM.
        /// </summary>
        /// <param name="serverName">The name of the server on which to create the Generation 2 VM.</param>
        /// <param name="vmName">The name of the VM to create.</param>
        internal static void
        DeleteGeneration2VM(
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