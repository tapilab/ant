# ANT: Artistic Network Toolbox

ANT is a library designed to enable humanities scholars to create interactive, dynamic network visualizations with no coding or database expertise.

Demos:
- [Raphael's Workshop](http://artisticnetworktoolkit.org/)
- [Chinese Export Markets](https://ant-china-8056b1db5341.herokuapp.com/network/)
- [Viceregal Americals](https://ant-spain-a79dfce9f9cd.herokuapp.com/network/)

To upload and explore your own data, use the [ANT Sandbox website](https://ant-sandbox-22f7f5795405.herokuapp.com/)

## Features


interactive interface to explore artistic connections | search and filter by keyword, time, and entity type
:-: | :-:
<video src="https://github.com/user-attachments/assets/a881cb51-ffd4-4f50-82d5-8afde57a97d5.mp4" width="200"></video> | <video src="https://github.com/user-attachments/assets/c767f943-7c11-4e25-b64b-b684e1313769.mp4" width="200"></video>









## Quickstart

To create a new website based on ANT using your own artistic dataset, please follow the steps below.

If you are not ready to setup a Heroku account, you can instead upload your spreadsheet to the [ANT Sandbox website](https://ant-sandbox-22f7f5795405.herokuapp.com/), which is temporary site to host and visualize your data for exploratory purposes.

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
