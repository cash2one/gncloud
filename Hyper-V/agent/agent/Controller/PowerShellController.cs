/**/

namespace com.gncloud.hyperv.agent.Controllers
{
    using System;
    using System.Web.Http;
    using com.gncloud.hyperv.agent.Service;

    public class PowerShellController : ApiController
    {
        
        [Route("powershell/execute")]
        [HttpGet]
        public String GetExecuteScript(String execute_script, String result_script)
        {
            PowerShellService ctrl = new PowerShellService();
            
            if (result_script != null)
            {
                ctrl.executePowerShellScript(execute_script);
                return ctrl.resultPowerShellScript(result_script);
            }
            else
            {
                return ctrl.resultPowerShellScript(execute_script);
            }
        }
    }
}