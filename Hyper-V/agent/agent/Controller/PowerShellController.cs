/**/

namespace com.gncloud.hyperv.agent.Controllers
{
    using System;
    using System.Web.Http;
    using com.gncloud.hyperv.agent.Service;

    public class PowerShellController : ApiController
    {
        
        [Route("powershell/execute")]
        [HttpPost]
        public String GetExecuteScript(String script)
        {
            PowerShellService ctrl = new PowerShellService();

            return ctrl.powerShellScript(script);
        }
    }
}