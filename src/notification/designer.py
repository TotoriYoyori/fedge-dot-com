from pathlib import Path
from typing import Annotated, Dict

from fastapi import Depends, Request
from jinja2 import Environment, FileSystemLoader

from src.notification.dependencies import craft_template_format
from src.notification.schemas import SendContext


class EmailDesigner:

    @staticmethod
    def write_email_html(
        request: Request, context: Annotated[dict, Depends(craft_template_format)]
    ) -> str:
        template_env = Environment(
            loader=FileSystemLoader(str(Path(__file__).parent / "templates"))
        )
        template_env.globals["url_for"] = request.url_for

        template = template_env.get_template("ho_2.html")
        return template.render(**context)

    @staticmethod
    def write_email_plaintext(
        context: Annotated[dict, Depends(craft_template_format)],
    ) -> str:
        return f"""
    Hi {context.name},

    This is a friendly reminder to book your {context.treatment}.

    We look forward to seeing you soon!
    """

    @staticmethod
    def format_html_template(data: Dict[str, str], html_template: str) -> str:
        """
        Inject pre-built HTML email template (containing inline CSS) with variables to customize.

        :param data: The data to inject. Matching keys will be injected to HTML template.
        :param html_template: The HTML template to use.
        """
        name = data.get("name", "there")
        treatment = data.get("treatment", "your wellness service")
        booking_link = data.get(
            "booking_link", "https://www.bokadirekt.se"  # placeholder
        )

        html = """
        HTML email template styled to match the aesthetic of hannaong.se.
        """
        name = data.get("name", "there").split()[0]
        treatment = data.get("treatment_selected", "your wellness service").title()
        order_number = data.get("order_number", "")
        location = data.get("location", "")

        html = f"""
        <!doctype html>
        <html lang="sv">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Booking Reminder</title>
          </head>
          <body style="margin: 20px; padding: 20px; background-color: #fdf9f6;">
            <!-- Outer wrapper table to center the content -->
            <table width="100%" style="background-color: #fdf9f6; padding: 20px 0; margin: 20px 0;
            border-collapse: collapse; text-align: center;">
              <tr>
                <td>
                  <!-- Main content table -->
                  <table width="600" style="background-color: #ffffff; border-radius: 10px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 40px; border-collapse: collapse;
                        font-family: 'Garamond', Helvetica, Arial, sans-serif; margin: 0 auto;">

                    <!-- Main content row -->
                    <tr>
                      <td style="text-align: center;">

                        <h1 style="color: #333333; margin-bottom: 10px;">Hanna & Ong</h1>
                        <h2>Hej {name}, tack för att du bokade hos oss!</h2>
                        <p style="color: #555555; font-size: 16px; line-height: 1.5;">
                          Du har obokad din beställning för <strong>{treatment}</strong> 
                          hos oss på <strong>{location}.</strong>
                        </p>
                        <p style="color: #555555; font-size: 16px; line-height: 1.5;">
                          Välj en av våra platser nedan för att boka din tid:
                        </p>

                        <!-- Buttons -->
                        <p style="margin: 30px 0;">
                          <a href="https://www.bokadirekt.se/places/hanna-ong-therapy-art-limhamn-malmo-55196"
                             style="background-color: #d8b4a0; color: #ffffff; text-decoration: none;
                             padding: 12px 24px; margin: 12px; border-radius: 5px; font-weight: bold; display: inline-block;
                             width: 120px; text-align: center;">
                            Malmö
                          </a>
                          <a href="https://www.bokadirekt.se/places/hanna-ong-therapy-art-helsingborg-39960"
                             style="background-color: #d8b4a0; color: #ffffff; text-decoration: none;
                             padding: 12px 24px; margin: 12px; border-radius: 5px; font-weight: bold; display: inline-block;
                             width: 120px; text-align: center;">
                            Helsingborg
                          </a>
                        </p>

                        <p style="color: #999999; font-size: 14px;">
                          Vi ser fram emot att välkomna dig snart!
                        </p>
                        <hr style="border: none; border-top: 1px solid #eeeeee; margin: 40px 0;" />
                        <p style="color: #aaaaaa; font-size: 12px;">
                          Om du redan har bokat hos oss, ignorera gärna detta meddelande
                        </p>
                        <p style="color: #aaaaaa; font-size: 12px;">
                          Ordernummer: {order_number}
                        </p>
                      </td>
                    </tr>

                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """
        return html

    @staticmethod
    def save_preview_html(filename: str, data: Dict[str, str]):
        html = render_html_template(data)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Preview saved to: {filename}")

    # ------------- READ_CSV -------------
    @staticmethod
    def sample_customer(csv_file: str) -> list[dict]:
        df = pd.read_csv(csv_file)
        df = df.query("not is_cancel").sample(5)

        result = []
        for i, row in df.iterrows():
            data = {
                "date": row["date"],
                "name": row["full_name"],
                "email": row["office_email"],
                "order_number": row["order_number"],
                "treatment_selected": row["treatment_selected"],
                "location": row["location"],
            }
            result.append(data)

        return result

    # ------------- SIMPLE DEMO USAGE ------------------
    # if __name__ == "__main__":
    #     # Example recipient data (you can modify this)
    #     customer_data_list = [
    #         {
    #             "date": "2026.01.02",
    #             "name": "Hanna Nguyen",
    #             "email": "info@hanna-ong.com",
    #             "order_number": "bbbb7:1212121",
    #             "treatment_selected": "deep therapy massage, basketball massage, foot massage",
    #             "location": "Limhamn",
    #         },
    #     ]
    #     for customer_data in customer_data_list:
    #         send_email(
    #             subject=f"Hej {customer_data["name"].split()[0]}, du har hälsofördelar att dela med dig av hos oss!",
    #             to_email=customer_data["email"],  # <-- change this
    #             from_email="teainbasement@gmail.com",  # <-- optional override
    #             data=customer_data,
    #         )
