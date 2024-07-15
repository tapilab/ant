# ANT: Artistic Network Toolkit

ANT is a library designed to enable humanities scholars to create interactive, dynamic network visualizations with no coding or database expertise.

For a demo, see https://www.artisticnetworktoolkit.org/.

## Quickstart

1. Copy the [Ant Template](https://docs.google.com/spreadsheets/d/1_8s2AoH53qPSzP2bNYMtFqfsp6Y8E91laCpQ9v83hYw/edit?usp=drive_link) Google Sheet to your Google Drive (`File->Make a Copy`)
2. Follow the instructions in the Template to populate a relational database.
3. Create a link to your sheet that is viewable, but not editable, by anyone (`Share->Anyone on the internet with the link can view`)
4. Click this button [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/tapilab/ant/tree/main) to copy the ANT code to a new Heroku server that will host your website. You'll need to create a Heroku account if you don't have one already.
    - **NB:** ANT is configured for the cheapest tier of Heroku server, which is $5/month.
    - Give the app any name that you like. The other fields can remain as their defaults. Click "Deploy app" to create the website.
5. After Heroku has finished deploying the site (~5 minutes), you can now access it at the website specified by heroku, which will be in the format: https://ant-demo-xxxxxx.herokuapp.com/ .
6. Click on the "Configure" button.
7. Paste in the link to your Google Sheet (See step #3 above).
8. The data will be imported from the sheet into a  PostgreSQL database on Heroku. Any warnings or errors will be printed to the screen.
9. Your site is ready!

### Sponsors

This project is supported by the National Endowment for the Humanities under Digital Humanities Advancement Grant #HAA-296281-24, by Tulane University's Newcomb Institute, and by Tulane's Lavin Bernick Grant program.

<table border=0>
  <tr>
    <td><img src="https://neh.gov/themes/gesso/images/logo-header.svg" width=200/></td>
    <td><img src="https://communications.tulane.edu/sites/default/files/pictures/TU.CTR_2c.png" width=200/></td>
  </tr>
</table>
