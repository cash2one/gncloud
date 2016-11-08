// THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
// ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
// PARTICULAR PURPOSE.
//
// Copyright (c) Microsoft. All rights reserved.

namespace test
{
    using System;
    using System.Globalization;
    using System.Management;
    using System.Reflection;
    using System.Collections.Generic;
    using Microsoft.Samples.HyperV.Common;
    using Microsoft.Samples.HyperV.AppHealth;
    using Microsoft.Samples.HyperV.EnhancedSession;
    using Microsoft.Samples.HyperV.FibreChannel;
    using Microsoft.Samples.HyperV.Generation2VM;
    using Microsoft.Samples.HyperV.IntegrationServices;
    using Microsoft.Samples.HyperV.Metrics;
    using Microsoft.Samples.HyperV.Migration;
    using Microsoft.Samples.HyperV.Networking;
    using Microsoft.Samples.HyperV.Replica;
    using Microsoft.Samples.HyperV.ResourcePools;
    using Microsoft.Samples.HyperV.PVM;
    using Microsoft.Samples.HyperV.Slp;
    using Microsoft.Samples.HyperV.Storage;
    using Microsoft.Samples.HyperV.StorageQoS;
    using Microsoft.Samples.HyperV.VmOperations;

    class Program
    {
        static void Main(string[] args)
        {
            //string hostName = "localhost";
            string hostName = ".";
            string vmName = "testvm";
            string first = "\\AcpiEx(VMBus,0,0)\\VenHw(9B17E5A2-0891-42DD-B653-80B5C22809BA,635161F83EDFC546913FF2D2F965ED0EDEC0CDF01C45974892F6A09D14FF12DC)\\MAC(000000000000)";

            /* VM 생성 */
            Console.WriteLine("---- CreateGeneration2VM ----");
            Generation2VMCreateSample.CreateGeneration2VM(hostName, vmName);
            
            /* VM 삭제 */
            Console.WriteLine("---- DeleteGeneration2VM ----");
            Generation2VMDeleteSample.DeleteGeneration2VM(hostName, vmName);
            //ImportUtilities.RemovePvm(vmName);

            /*
            Console.WriteLine("---- GetVMGeneration ----");
            Generation2VMGetSample.GetVMGeneration(hostName, vmName);

            Console.WriteLine("---- GetGeneration2BootOrder ----");
            Generation2VMGetBootOrderSample.GetGeneration2BootOrder(hostName, vmName);

            Console.WriteLine("---- GetGeneration2SecureBoot ----");
            Generation2VMGetSecureBootSample.GetGeneration2SecureBoot(hostName, vmName);

            Console.WriteLine("---- GetPauseAfterBootFailure ----");
            Generation2VMGetPauseAfterBootFailureSample.GetPauseAfterBootFailure(hostName, vmName);

            Console.WriteLine("---- SetGeneration2BootOrder ----");
            Generation2VMSetBootOrderSample.SetGeneration2BootOrder(hostName, vmName, first);
            
            Console.WriteLine("---- SetGeneration2SecureBoot ----");
            Generation2VMSetSecureBootSample.SetGeneration2SecureBoot(hostName, vmName, true);
            */
        }
    }
}
