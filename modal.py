import discord

options = [discord.SelectOption(label="None"), discord.SelectOption(label="Medium"), discord.SelectOption(label="Advanced")]

class RegisterModal(discord.ui.Modal, title="Register"):
    user_nickname = discord.ui.TextInput(label="Please enter your prefered nickname.", required=True, max_length=50, style=discord.TextStyle.short)
    user_pronouns = discord.ui.TextInput(label="Please enter your prefered pronouns.", required=True, max_length=50, style=discord.TextStyle.short)

    registered_users = []

    async def on_submit(self, interaction: discord.Interaction) -> None:
        select = discord.ui.Select(placeholder="What is your DnD expereince?", options=options)
        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message("Please submit a response.", view=view, ephemeral=True)

        @discord.ui.select()
        async def select_callback(interaction):
            if interaction.user.id not in self.registered_users:
                log = discord.utils.get(interaction.guild.channels, name="log")
                await log.send(f"User {interaction.user.name} registered.\nID: {interaction.user.id}, \nNickname: {self.user_nickname}, \nPronouns: {self.user_pronouns}, \nExperience: {select.values[0]}")
                await interaction.response.send_message(f"Thank you for registering!", ephemeral=True)
                self.registered_users.append(interaction.user.id)
            else:
                await interaction.response.send_message(f"You have already registered!", ephemeral=True)

        select.callback = select_callback
    