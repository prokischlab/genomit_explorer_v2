import dash
from dash import html, dcc

dash.register_page(__name__, path='/data_protection', order=6)

layout = html.Div(children=[
    html.Div([
        html.H1(children='Data protection statement'),
        html.Br(),

        html.P(html.B('Data protection declaration')),
        html.P('Responsible body within the meaning of data protection laws, '
               'in particular the EU Data Protection Ordinance (DSGVO):', ),
        html.Ul([
            html.Li('Dr. Holger Prokisch')
        ]),

        html.P(html.B('Your rights as a party concerned')),
        html.P('You can exercise the following rights at any time using '
               'the contact details provided by our data protection officer:', ),
        html.Ul([
            html.Li('Information about your data stored with us and their processing'),
            html.Li('Correction of incorrect personal data'),
            html.Li('Deletion of your data stored with us'),
            html.Li('Restriction of data processing if we are not yet '
                    'allowed to delete your data due to legal obligations'),
            html.Li('Objection to the processing of your data by us'),
            html.Li('Data transferability if you have consented to data '
                    'processing or have concluded a contract with us'),
        ]),
        html.P('If you have given us your consent, you can revoke it at any time with effect for the future.', ),
        html.P('You can contact your local supervisory authority at any time with a complaint. '
               'Your competent supervisory authority depends on your state of residence, '
               'your work or the alleged infringement. A list of supervisory authorities (for the non-public sector) '
               'with addresses can be found at: '
               'https://www.bfdi.bund.de/DE/Infothek/Anschriften_Links/addresses_links-node.html.', ),

        html.P(html.B('Purposes of data processing by the responsible body and third parties')),
        html.P('We process your personal data only for the purposes stated in this data protection declaration. '
               'Your personal data will not be passed on to third parties for purposes other than those mentioned. '
               'We will only pass on your personal data to third parties if:', ),
        html.Ul([
            html.Li('you have given your express consent'),
            html.Li('processing is necessary to process a contract with you'),
            html.Li('the processing is necessary to fulfil a legal obligation'),
            html.Li('the processing is necessary to protect legitimate interests and there is no reason to believe '
                    'that you have an overriding interest worthy of protection in not disclosing your data'),
        ]),

        html.P(html.B('Deletion or blocking of data')),
        html.P('We adhere to the principles of data avoidance and data economy. '
               'We therefore only store your personal data for as long as is necessary to achieve the purposes '
               'stated here or as provided for in the various storage periods provided for by law. '
               'After the respective purpose or expiry of these periods, the corresponding data will be blocked or '
               'deleted as a matter of routine and in accordance with statutory regulations.', ),

        html.P(html.B('Cookies')),
        html.P('Like many other websites, we also use so-called “cookies”. '
               'Cookies are small text files that are transferred from a website server to your hard drive. '
               'This automatically provides us with certain data such as IP address, '
               'browser used, operating system and your connection to the Internet.', ),
        html.P('Cookies cannot be used to start programs or to transmit viruses to a computer. '
               'Based on the information contained in cookies, we can make navigation easier for you '
               'and enable the correct display of our web pages.', ),
        html.P('Under no circumstances will the data we collect be passed on to third parties or '
               'linked to personal data without your consent.', ),
        html.P('Of course, you can also view our website without cookies. '
               'Internet browsers are regularly set to accept cookies. '
               'In general, you can deactivate the use of cookies at any time via the settings of your browser. '
               'Please use the help functions of your Internet browser to find out how you can change these settings. '
               'Please note that some features of our website may not work if you have disabled the use of cookies.', ),

        html.P(html.B('Changes to our data protection regulations')),
        html.P('We reserve the right to adapt this data protection declaration so that it always complies '
               'with current legal requirements or to implement changes to our services in the data protection '
               'declaration, e.g. when introducing new services. '
               'The new data protection declaration will then apply for your next visit.', ),

        html.P(html.B('Questions to the data protection officer')),
        html.P('If you have any questions about data protection, '
               'please contact the person responsible for data protection in our organisation directly: '
               'Dr Holger Prokisch.', ),
    ], style={"margin-left": "10%", "margin-right": "10%"})
])
