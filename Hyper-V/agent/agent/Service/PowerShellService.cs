

namespace com.gncloud.hyperv.agent.Service
{
    using System;
    using System.Globalization;
    using System.Collections;
    using System.Collections.Generic;
    using System.Collections.ObjectModel;
    using System.Management;
    using System.Management.Automation;
    using System.Text;
    //using log4net;
    //using log4net.Config;
    using System.Text.RegularExpressions;

    public class PowerShellService
    {
        //private static readonly ILog log = LogManager.GetLogger(typeof(PowerShellService));

        public PowerShellService()
        {
        }

        public void executePowerShellScript(String script)
        {
            //log.Info("Execute Script: " + script);
            // Execute PowerShell Script.
            Collection<PSObject> execute = PowerShell.Create()
                    .AddScript(script)
                    .Invoke();
        }

        public String resultPowerShellScript(String script)
        {
            //log.Info("Result Script: " + script);
            // Execute PowerShell Script for Result Value.
            Collection<PSObject> result = PowerShell.Create()
                    .AddScript(script)
                    .Invoke();

            return result[0].ToString();
        }
    }
}