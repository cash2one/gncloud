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
            service.createVM("jhjeon_test", "2", "3", "2096MB", "C:\\images\\windows_server_2012_r2.vhdx");
            service.startVM("jhjeon_test");
            //service.stopVM("jhjeon_test");
        }
    }
}
