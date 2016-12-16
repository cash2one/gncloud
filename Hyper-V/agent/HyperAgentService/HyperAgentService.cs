using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;
using System.Web.Http;
using System.Web.Http.SelfHost;
using System.Net.Http.Headers;

namespace HyperAgentService
{
    public partial class HyperAgentService : ServiceBase
    {
        HttpSelfHostServer server;

        public HyperAgentService()
        {
            InitializeComponent();

            this.CanStop = true;
            this.AutoLog = true;
        }

        public void OnDebug()
        {
            OnStart(null);
        }

        protected override void OnStart(string[] args)
        {

            using (System.IO.StreamWriter file = new System.IO.StreamWriter(AppDomain.CurrentDomain.BaseDirectory + "\\system.log"))
            {
                try
                {
                    var config = new HttpSelfHostConfiguration("http://127.0.0.1:" + Properties.Settings.Default.ProcessPort);
                    config.MapHttpAttributeRoutes();
                    /*
                    config.Routes.MapHttpRoute("API Default", "api/{controller}/{id}",
                        new { id = RouteParameter.Optional }
                    );
                    */

                    server = new HttpSelfHostServer(config);
                    server.OpenAsync().Wait();
                }
                catch (Exception ex)
                {
                    file.WriteLine("Exception: " + ex.Message);
                }
            }
        }

        protected override void OnStop()
        {
        }
    }
}
