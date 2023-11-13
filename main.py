import interactions
from interactions import StringSelectMenu, ModalContext
from interactions.api.events import Component
import os
from dotenv import load_dotenv
from src.airtable import get_record
from src.jira import create_ticket

load_dotenv()
token = os.getenv("token")
if not token:
    token = ""
bot = interactions.Client(token=token)

text_1 = "Please follow the strps in the guide Link - https://docs.torchlabs.xyz/errors-and-faq/discord/getting-an-auth-error-coming-when-accessing-to-user-dashboard \nPlease fill the following form once the steps in the guide are completed"

text_2 = """
**Step 1**
Delete old DNS records

**Step 2**
Follow the instruction in the guide - [Adding the site to the domain](<https://docs.torchlabs.xyz/onboarding-guide/adding-your-site-to-your-domain>)

**Step 3**
Follow the instruction in the guide  - [White labeling the proxies](<https://docs.torchlabs.xyz/onboarding-guide/white-labeling-proxies-with-your-domain>)

**Step 4**
Enter your new domain bellow
"""


@interactions.slash_command(name="bug", description="create a bug report")
async def bug(ctx):
    # Create a dropdown with issues
    components = StringSelectMenu(
        "Discord auth error",
        "Change the domain",
        "Reset Password",
        "other",
        placeholder="What issue are you facing",
        min_values=1,
        max_values=1,
        custom_id="issue"
    )
    # Send a message with the dropdown menu
    await ctx.send("Please select your issue:", components=components)


@interactions.listen(Component)
async def on_componenet(event: Component):
    ctx = event.ctx

    match ctx.custom_id:
        case "issue":
            match ctx.values[0]:
                case "Discord auth error":
                    await discord_auth_error(ctx)
                case "Change the domain":
                    await change_domain(ctx)
                case "Reset Password":
                    await reset_password(ctx)


email_button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Enter Email",
        custom_id="Email Button",
    )


async def reset_password(ctx):
    message = await ctx.send(
        "What is your TL admin dashboard login email?",
        components=email_button)
    try:
        email_button_response = await bot.wait_for_component(
            components=email_button, timeout=300)
    except TimeoutError:
        email_button.disabled = True
        await message.edit(components=email_button)
        return ()
    email_form = interactions.Modal(
        interactions.InputText(
            label="email",
            style=interactions.TextStyles.SHORT,
            custom_id="email_input",
            placeholder="example@mail.com"
        ),
        title="Email Form",
    )
    await email_button_response.ctx.send_modal(email_form)
    email_resaponse: ModalContext = await bot.wait_for_modal(email_form)
    email = email_resaponse.responses["email_input"]
    record = get_record(email)
    if not record:
        description = f"\nFailed to fetch airtable data {email}"
    else:
        description = f"\nairtable url: {record[0]}\nFirebase id: {record[1]}"
    await email_resaponse.send("Created your ticked you will recive a reset link shortly")
    create_ticket("Password resetting link", description)


async def change_domain(ctx):
    message = await ctx.send(
        "What is your TL admin dashboard login email?",
        components=email_button)
    try:
        email_button_response = await bot.wait_for_component(
            components=email_button, timeout=300)
    except TimeoutError:
        email_button.disabled = True
        await message.edit(components=email_button)
        return ()
    email_form = interactions.Modal(
        interactions.InputText(
            label="email",
            style=interactions.TextStyles.SHORT,
            custom_id="email_input",
            placeholder="example@mail.com"
        ),
        title="Email Form",
    )
    await email_button_response.ctx.send_modal(email_form)
    email_resaponse: ModalContext = await bot.wait_for_modal(email_form)
    email = email_resaponse.responses["email_input"]
    domain_button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Enter Domain",
        custom_id="enter_domain",
    )
    message = await email_resaponse.send(text_2, components=domain_button)
    print("done")
    try:
        domain_button_click = await bot.wait_for_component(
            components=domain_button, timeout=350)
    except TimeoutError:
        domain_button.disabled = True
        await message.edit(components=email_button)
        return ()
    domain_form = interactions.Modal(
        interactions.InputText(
            label="Domain",
            style=interactions.TextStyles.SHORT,
            custom_id="domain_input",
            placeholder="my.domain.com"
        ),
        title="Domain Form",
    )
    await domain_button_click.ctx.send_modal(domain_form)
    domain_response: ModalContext = await bot.wait_for_modal(domain_form)
    domain = domain_response.responses["domain_input"]
    record = get_record(email)
    description = f"Domain: {domain}"
    if not record:
        description += f"\nFailed to fetch airtable data {email}"
    else:
        description += f"\nairtable url: {record[0]}\nFirebase id: {record[1]}"
    await domain_response.send("Your ticket has been created!")
    create_ticket("Update Killer dash records", description)
    


async def discord_auth_error(ctx):
    form_button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Open Form",
        custom_id="form_button",
    )

    async def send_details_form(component: Component):
        details_form = interactions.Modal(
            interactions.InputText(
                label="Client ID",
                style=interactions.TextStyles.SHORT,
                custom_id="client_id",
            ),
            interactions.InputText(
                label="Client Secret",
                style=interactions.TextStyles.SHORT,
                custom_id="client_secret",
            ),
            interactions.InputText(
                label="Redirect URL",
                style=interactions.TextStyles.SHORT,
                custom_id="redirect_url",
            ),
            interactions.InputText(
                label="Server ID",
                style=interactions.TextStyles.SHORT,
                custom_id="server_id",
            ),
            title="Details",
        )
        await component.ctx.send_modal(details_form)
        detail_response: ModalContext = await bot.wait_for_modal(details_form)
        client_id = detail_response.responses["client_id"]
        client_secret = detail_response.responses["client_secret"]
        redirect_url = detail_response.responses["redirect_url"]
        server_id = detail_response.responses["server_id"]
        await detail_response.send("Created your ticket")
        return (client_id, client_secret, redirect_url, server_id)

    async def send_email_form(component: Component):
        email_form = interactions.Modal(
            interactions.InputText(
                label="email",
                style=interactions.TextStyles.SHORT,
                custom_id="email_input",
                placeholder="example@mail.com"
            ),
            title="Email Form",
        )
        await component.ctx.send_modal(email_form)
        email_resaponse: ModalContext = await bot.wait_for_modal(email_form)
        global email
        email = email_resaponse.responses["email_input"]

        email_resaponse_message = await email_resaponse.send(text_1, components=form_button)
        try:
            open_form_btt = await bot.wait_for_component(components=form_button,  timeout=300)
            client_id, client_secret, redirect_url, server_id = await send_details_form(open_form_btt)
            print(email, client_id, client_secret, redirect_url, server_id)
            record = get_record(email)
            description = f"""
            client_id: {client_id}
            client_secret: {client_secret}
            redirect_url: {redirect_url}
            server_id: {server_id}"""
            if not record:
                description += f"\nFailed to fetch airtable data {email}"
            else:
                description += f"""
                airtable url: {record[0]}
                "Firebase id: {record[1]}"
                """
            create_ticket("Update discord Authentication", description)
        except TimeoutError:
            form_button.disabled = True
            await email_resaponse_message.edit(components=form_button)

    message = await ctx.send("What is your TL admin dashboard login email?",
                             components=email_button)
    try:
        await bot.wait_for_component(
            components=email_button, check=send_email_form, timeout=300)
    except TimeoutError:
        email_button.disabled = True
        await message.edit(components=email_button)


bot.start()
