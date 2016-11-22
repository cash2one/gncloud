/**
 * 작성자: 전제현
 * 
 */

namespace com.gncloud.HyperV.Agent.Script
{
    using System;
    using System.Globalization;
    using System.Collections;
    using System.Collections.Generic;
    using System.Collections.ObjectModel;
    using System.Management;
    using System.Management.Automation;

    class HyperVScript
    {
        public 
        HyperVScript()
        {
        }

        public string
        NewVM(
            string name,
            long generation)
        {
            string script = "New-VM";
            script += " " + name;
            script += " -Generation " + generation;
            script += " | Convertto-Json";

            Collection<PSObject> result = PowerShell.Create()
                    .AddScript(script)
                    .Invoke();
            Console.WriteLine(result[0].ToString());

            return result[0].ToString();
        }

        public string
        SetVM(
            string vmName,
            long processorCount,
            long memoryStartupBytes)
        {
            string script1 = "Set-VM";
            script1 += " " + vmName;
            script1 += " -ProcessorCount " + processorCount + " ";
            script1 += " -MemoryStartupBytes " + memoryStartupBytes + "MB";

            PowerShell.Create()
                    .AddScript(script1)
                    .Invoke();

            string script2 = "Get-VM " + vmName;
            script2 += " | Convertto-Json";

            Collection<PSObject> result = PowerShell.Create()
                    .AddScript(script2)
                    .Invoke();

            return result[0].ToString();
        }

        public string
        ConvertVHD(
            string original_vhd,
            string copy_vhd)
        {
            string script1 = "Convert-VHD";
            script1 += " -Path " + original_vhd + " ";
            script1 += " -DestinationPath " + copy_vhd;

            PowerShell.Create()
                    .AddScript(script1)
                    .Invoke();

            string script2 = "Get-VHD " + copy_vhd;
            script2 += " | Convertto-Json";

            Collection<PSObject> result = PowerShell.Create()
                    .AddScript(script2)
                    .Invoke();

            return result[0].ToString();
        }

        public string
        AddVMHardDiskDrive(
            string vmName,
            string path)
        {
            string script1 = "Add-VMHardDiskDrive";
            script1 += " -VMName " + vmName + " ";
            script1 += " -Path " + path;

            PowerShell.Create()
                    .AddScript(script1)
                    .Invoke();

            string script2 = "Get-VM " + vmName;
            script2 += " | Convertto-Json";

            Collection<PSObject> result = PowerShell.Create()
                    .AddScript(script2)
                    .Invoke();

            return result[0].ToString();
        }
    }
}
