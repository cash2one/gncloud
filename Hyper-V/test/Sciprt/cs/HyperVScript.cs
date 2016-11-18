/**
 * 작성자: 전제현
 * 
 */

namespace com.gncloud.HyperV.Agent.Script
{
    using System;
    using System.Globalization;
    using System.Management;
    using System.Management.Automation;

    static class HyperVScript
    {
        internal static void
        NewVM(
            string name,
            string generation)
        {
            string script = "New-VM";
            script += " " + name;
            script += " -Generation " + generation;

            PowerShell.Create()
                    .AddScript(script)
                    .Invoke();
        }

        internal static void
        SetVM(
            string vmName,
            string processorCount,
            string memoryStartupBytes)
        {
            string script = "Set-VM";
            script += " " + vmName;
            script += " -ProcessorCount " + processorCount + " ";
            script += " -MemoryStartupBytes " + memoryStartupBytes;

            PowerShell.Create()
                    .AddScript(script)
                    .Invoke();
        }

        internal static void
        AddVMHardDiskDrive(
            string vmName,
            string path)
        {
            string script = "Add-VMHardDiskDrive";
            script += " -VMName " + vmName + " ";
            script += " -Path " + path;

            PowerShell.Create()
                    .AddScript(script)
                    .Invoke();
        }
    }
}
