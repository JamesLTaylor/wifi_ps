// GetWifiInfo.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <windows.h>
#include <wlanapi.h>
#include <objbase.h>
#include <wtypes.h>
#include <iostream>
#include <string>

#include <stdio.h>
#include <stdlib.h>
#include "GetWifiInfo.h"

// Need to link with Wlanapi.lib and Ole32.lib
#pragma comment(lib, "wlanapi.lib")
#pragma comment(lib, "ole32.lib")

bool scanDone = false;


static VOID WINAPI WlanNotification(WLAN_NOTIFICATION_DATA *wlanNotifData, VOID *p)
{
	if (wlanNotifData->NotificationCode == wlan_notification_acm_scan_complete)
	{
		scanDone = true;
	}
}


int main(int argc, char* argv[])
{
	bool doScan;
	if (argc != 2) {
		std::cerr << "Argument must be scan=yes or scan=no" << std::endl;
		return 1;
	}
	if (std::string(argv[1]) == "scan=yes") {
		doScan = true;
	}
	else if (std::string(argv[1]) == "scan=no") {
		doScan = false;
	}
	else {
		std::cerr << "Argument must be scan=yes or scan=no" << std::endl;
		return 1;
	}


	HANDLE hClient = NULL;
	DWORD dwResult = 0;
	DWORD dwMaxClient = 2;
	DWORD dwCurVersion = 0;

	PWLAN_BSS_LIST ppWlanBssList = NULL;
	PWLAN_INTERFACE_INFO_LIST pIfList = NULL;
	PWLAN_INTERFACE_INFO pIfInfo = NULL;



	dwResult = WlanOpenHandle(dwMaxClient, NULL, &dwCurVersion, &hClient);
	dwResult = WlanEnumInterfaces(hClient, NULL, &pIfList);

	pIfInfo = (WLAN_INTERFACE_INFO *)&pIfList->InterfaceInfo[0];

	if (doScan) {
		dwResult = WlanRegisterNotification(hClient, WLAN_NOTIFICATION_SOURCE_ACM, TRUE, &WlanNotification, NULL, 0, NULL);
		DWORD ignore = WlanScan(hClient, &pIfInfo->InterfaceGuid, NULL, NULL, NULL);

		while (!scanDone)
		{
			Sleep(50);
		}
		Sleep(50);
	}

	dwResult = WlanGetNetworkBssList(hClient,
		&pIfInfo->InterfaceGuid,
		NULL, dot11_BSS_type_any, NULL, NULL,
		&ppWlanBssList);

	for (unsigned int j = 0; j < ppWlanBssList->dwNumberOfItems; j++) {
		_WLAN_BSS_ENTRY entry = (_WLAN_BSS_ENTRY)ppWlanBssList->wlanBssEntries[j];
		if (entry.dot11Ssid.uSSIDLength == 0)
			wprintf(L"");
		else {
			for (unsigned int k = 0; k < entry.dot11Ssid.uSSIDLength; k++) {
				wprintf(L"%c", (int)entry.dot11Ssid.ucSSID[k]);
			}			
		}
		wprintf(L",%ld,", entry.lRssi);
		for (unsigned int k = 0; k<6; k++)
		{
			wprintf(L"%02x", entry.dot11Bssid[k]);
			if (k<5) wprintf(L"-");
		}
		wprintf(L"\n");
	}
}

