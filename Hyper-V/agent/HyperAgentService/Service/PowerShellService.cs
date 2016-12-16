

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

        public String powerShellScript(String script)
        {
            //log.Info("Result Script: " + script);
            // Execute PowerShell Script for Result Value.
            Collection<PSObject> result = PowerShell.Create()
                    .AddScript(script)
                    .Invoke();

            if (result.Count == 0)
            {
                return "{}";
            }
            else
            {
                return result[0].ToString();
            }
        }
    }
}