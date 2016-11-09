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

    static class Generation2VMStopSample
    {
        /// <summary>
        /// Create a Generation 2 VM.
        /// </summary>
        /// <param name="serverName">The name of the server on which to create the Generation 2 VM.</param>
        /// <param name="vmName">The name of the VM to create.</param>
        internal static void
        StopGeneration2VM(
            string serverName,
            string vmName)
        {
            ManagementScope scope = new ManagementScope(@"\\" + serverName + @"\root\virtualization\v2", null);

            using (ManagementObject vm = WmiUtilities.GetVirtualMachine(vmName, scope))
            using (ManagementBaseObject inParams = vm.GetMethodParameters("RequestStateChange"))
            {
                inParams["RequestedState"] = 3;

                using (ManagementBaseObject outParams =
                    vm.InvokeMethod("RequestStateChange", inParams, null))
                {
                    WmiUtilities.ValidateOutput(outParams, scope);
                }
            }
        }
    }
}