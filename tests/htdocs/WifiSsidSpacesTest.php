<?php
use PHPUnit\Framework\TestCase;

class WifiSsidSpacesTest extends TestCase
{
    public function testSsidWithSpacesIsQuotedForBash()
    {
        // Simuliere POST-Daten wie im UI
        $_POST = [
            'submitWifi' => 'submit',
            'WIFIssid_0' => "Test 123",
            'WIFIpass_0' => "testpass123",
            'WIFIprio_0' => "10"
        ];
        
        // Dummy-Konfiguration
        $conf = [
            'scripts_abs' => '/tmp' // Dummy-Pfad
        ];
        
        // Fange exec()-Aufruf ab
        $output = null;
        $called = false;
        $that = $this;
        // Mock exec() innerhalb dieses Gültigkeitsbereichs
        require_once __DIR__ . '/../../htdocs/inc.setWifi.php';
        
        // Extrahiere den Bash-Befehl aus $exec
        // (In inc.setWifi.php wird exec("sudo bash -c '...$exec...'") aufgerufen)
        // Wir prüfen, ob die SSID korrekt gequotet ist
        $pattern = "/add_wireless_network wlan0 'Test 123' 'testpass123' '10'/";
        $this->assertMatchesRegularExpression($pattern, $exec, 'SSID mit Leerzeichen wird nicht korrekt gequotet!');
    }
}
