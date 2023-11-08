import interactions
from interactions import StringSelectMenu, ModalContext
from interactions.api.events import Component
import os
from dotenv import load_dotenv
from interactions.models.discord import components

load_dotenv()
token = os.getenv("token")
if not token:
    token = ""
bot = interactions.Client(token=token)


@interactions.slash_command(name="bug", description="create a bug report")
async def bug(ctx):
    # Create a dropdown with issues
    components = StringSelectMenu(
        "Discord auth error", "other",
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
        detail_response : ModalContext = await bot.wait_for_modal(details_form)
        client_id = detail_response.responses["client_id"]
        client_secret = detail_response.responses["client_secret"]
        redirect_url = detail_response.responses["redirect_url"]
        server_id = detail_response.responses["server_id"]
        await detail_response.send("Creating your ticket")
        print(client_id, client_secret, redirect_url, server_id)

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
        email = email_resaponse.responses["email_input"]
        email_resaponse_message = await email_resaponse.send("Please follow the strps in the guide Link - https://docs.torchlabs.xyz/errors-and-faq/discord/getting-an-auth-error-coming-when-accessing-to-user-dashboard \nPlease fill the following form once the steps in the guide are completed",components=form_button)
        try:
            await bot.wait_for_component(
                components=form_button, check=send_details_form, timeout=300)
        except TimeoutError:
            form_button.disabled = True
            await email_resaponse_message.edit(components=form_button)

    email_button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Enter Email",
        custom_id="Email Button",
    )
    message = await ctx.send("What is your TL admin dashboard login email?",
                             components=email_button)
    try:
        await bot.wait_for_component(
            components=email_button, check=send_email_form, timeout=300)
    except TimeoutError:
        email_button.disabled = True
        await message.edit(components=email_button)


bot.start()
