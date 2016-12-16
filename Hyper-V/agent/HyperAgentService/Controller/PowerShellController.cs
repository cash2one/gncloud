/**/

namespace com.gncloud.hyperv.agent.Controllers
{
    using System;
    using System.Web.Http;
    using com.gncloud.hyperv.agent.Service;

    public class PowerShellController : ApiController
    {
        [Route("service/check")]
        [HttpGet]
        public String CheckService()
        {
            return "{\"message\":\"Service Check OK.\"}";
        }

        [Route("powershell/execute")]
        [HttpPost]
        public String GetExecuteScript(String script)
        {
            PowerShellService ctrl = new PowerShellService();

            return ctrl.powerShellScript(script);
        }
    }
}