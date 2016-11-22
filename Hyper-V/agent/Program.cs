// THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
// ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
// PARTICULAR PURPOSE.
//
// Copyright (c) Microsoft. All rights reserved.

namespace com.gncloud.HyperV.Agent
{
    using System;
    using System.Globalization;
    using System.Management;
    using System.Reflection;
    using System.Collections.Generic;
    using com.gncloud.HyperV.Agent.Service;

    class Program
    {
        static void Main(string[] args)
        {
            HyperVService service = new HyperVService(".");

            string vmName = "testvm";

            Console.WriteLine("--- NewVM ---");
            Console.WriteLine(service.NewVM(vmName, 2));
            Console.WriteLine("--- SetVM ---");
            Console.WriteLine(service.SetVM(vmName, 3, 2096));
            Console.WriteLine("--- ConvertVHD ---");
            Console.WriteLine(service.ConvertVHD(1, vmName, "winsv2012r2"));
            Console.WriteLine("--- AddVMHardDiskDrive ---");
            Console.WriteLine(service.AddVMHardDiskDrive(1, vmName, "winsv2012r2"));
            Console.WriteLine("--- StartVM ---");
            service.startVM(vmName);
            //service.stopVM("jhjeon_test");
        }
    }
}
