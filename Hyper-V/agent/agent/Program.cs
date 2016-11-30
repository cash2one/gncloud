using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Web.Http;
using System.Web.Http.SelfHost;
using System.Net.Http.Headers;

namespace agent
{
    class Program
    {

        static void Main(string[] args)
        {
            var config = new HttpSelfHostConfiguration("http://127.0.0.1:" + agent.Properties.Settings.Default.ProcessPort);

            config.MapHttpAttributeRoutes();

            //config.Formatters.Add(new BrowserJsonFormatter());

            /*
            config.Routes.MapHttpRoute("API Default", "api/{controller}/{id}",
                new { id = RouteParameter.Optional }
            );
            */

            using (HttpSelfHostServer server = new HttpSelfHostServer(config))
            {
                server.OpenAsync().Wait();
                Console.WriteLine("Press Enter to quit.");
                Console.ReadLine();
            }
        }
    }
}
