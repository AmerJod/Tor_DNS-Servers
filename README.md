# README #

# A Dynamic Test-Suite for DNS Resilience - 10/08/2018

UCL - Project
This project is part of dissertation 'A Dynamic Test-Suite for DNS Resilience' at UNIVERSITY COLLEGE LONDON.

A Dynamic Test-Suite for DNS Resilience - Python Project DNS_Project

This project has been implemented by Amer Joudiah as part of his dissertation.

This program has been built using python (PyCharm 2018.1)


### This project is consist of three main parts: ###

1- TORMAPPER Tools

    1- Enumerate all the TOR exit nodes.

    2- Enumerate all the DNS resolver servers that are used by TOR network.

    3- Generate some statistics that help to find the most vulnerable DNS servers.

    4- Has 3 different modes:
            1- TOR connection checker: check if the exit node is accebele
            2- DNS 0x20-bit encoding checker: check if the DNS servers that are used by the TOR network have
               implemented 0x20-bit encoding countermeasure.
            3- DNS statistic generator: generate DNS statistics about the port number and the requests Id
               that have been used.

2- DNS Server:

    1- Work like an ordinary DNS Server, where it resolves only IPv4 requests.

    2- Log all the incoming requests.

    3- Has the ability to distinction between transactions by depending on the sub-domain.

    4- Has the ability to work as as adversary that can forge DNS replies (Port number or sendRequests ID)

3- Web Server:

    1- Work like an ordinary Web Server, where my website is hosted.

    2- Log all the incoming requests.

