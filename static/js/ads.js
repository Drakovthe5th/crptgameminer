class AdManager {
    constructor({ userId, country }) {
        this.userId = userId;
        this.country = country;
        this.adBlockDetected = false;
        this.checkAdBlock();
    }
    
    // Ad block detection
    checkAdBlock() {
        const testAd = document.createElement('div');
        testAd.innerHTML = '&nbsp;';
        testAd.className = 'adsbox';
        document.body.appendChild(testAd);
        
        setTimeout(() => {
            if (testAd.offsetHeight === 0) {
                this.adBlockDetected = true;
                this.handleAdBlock();
            }
            document.body.removeChild(testAd);
        }, 100);
    }
    
    handleAdBlock() {
        const adContainer = document.getElementById('ad-container');
        adContainer.innerHTML = `
            <div class="ad-alternative">
                <p>Ad blocker detected. Support us by enabling ads!</p>
                <button onclick="location.reload()">Reload with Ads</button>
            </div>
        `;
    }
    
    // Geo-targeted ad selection
    selectAdPlatform() {
        // High CPM countries get premium ads
        if (config.HIGH_CPM_COUNTRIES.includes(this.country)) {
            return 'coinzilla';
        }
        
        // Crypto-focused countries
        const cryptoCountries = ['RU', 'UA', 'TR', 'VN', 'BR', 'IN'];
        if (cryptoCountries.includes(this.country)) {
            return 'a-ads';
        }
        
        // Default to PropellerAds
        return 'propeller';
    }
    
    // Load ad implementation
    loadAd() {
        if (this.adBlockDetected) return;
        
        const platform = this.selectAdPlatform();
        let adScript = '';
        
        switch(platform) {
            case 'coinzilla':
                adScript = `
                    <div id="coinzilla-ad" data-zone="${config.COINZILLA_PUB_ID}"></div>
                    <script>
                        (function() {
                            const czScript = document.createElement('script');
                            czScript.async = true;
                            czScript.src = 'https://coinzilla.com/scripts/banner.js';
                            document.head.appendChild(czScript);
                        })();
                    </script>
                `;
                break;
                
            case 'propeller':
                adScript = `
                    <div id="propeller-ad"></div>
                    <script>
                        (function() {
                            const ppScript = document.createElement('script');
                            ppScript.src = 'https://ads.propellerads.com/v5/${config.PROPELLER_ZONE_ID}';
                            document.head.appendChild(ppScript);
                        })();
                    </script>
                `;
                break;
                
            case 'a-ads':
                adScript = `
                    <div id="a-ads-ad"></div>
                    <script>
                        (function() {
                            const aaScript = document.createElement('script');
                            aaScript.src = 'https://a-ads.com/${config.A_ADS_ZONE_ID}';
                            document.head.appendChild(aaScript);
                        })();
                    </script>
                `;
                break;
        }
        
        document.getElementById('ad-container').innerHTML = adScript;
        this.trackImpression(platform, 'banner');
    }
    
    // Rewarded ad flow
    showRewardedAd() {
        const platform = this.selectAdPlatform();
        let rewardHandler;
        
        switch(platform) {
            case 'coinzilla':
                rewardHandler = this.showCoinzillaRewarded();
                break;
                
            case 'propeller':
                rewardHandler = this.showPropellerRewarded();
                break;
                
            case 'a-ads':
                rewardHandler = this.showAAdsRewarded();
                break;
        }
        
        rewardHandler.catch(error => {
            console.error('Rewarded ad failed:', error);
            Telegram.WebApp.showAlert('Ad failed to load. Please try again.');
        });
    }
    
    showCoinzillaRewarded() {
        return new Promise((resolve, reject) => {
            // Coinzilla rewarded implementation
            Telegram.WebApp.showAlert('Watch a short video to earn rewards!');
            // Simulate ad completion
            setTimeout(() => {
                this.grantReward('coinzilla');
                resolve();
            }, 3000);
        });
    }
    
    showPropellerRewarded() {
        return new Promise((resolve, reject) => {
            // PropellerAds implementation
            Telegram.WebApp.showAlert('Watch a short video to earn rewards!');
            // Simulate ad completion
            setTimeout(() => {
                this.grantReward('propeller');
                resolve();
            }, 3000);
        });
    }
    
    showAAdsRewarded() {
        return new Promise((resolve, reject) => {
            // A-ADS implementation
            Telegram.WebApp.showAlert('Watch a short video to earn rewards!');
            // Simulate ad completion
            setTimeout(() => {
                this.grantReward('a-ads');
                resolve();
            }, 3000);
        });
    }
    
    grantReward(platform) {
        fetch('/miniapp/ad-reward', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-User': this.userId
            },
            body: JSON.stringify({ platform: platform })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const message = `You earned ${data.reward.toFixed(6)} XNO! ${data.weekend_boost ? '(Weekend Boost Active!)' : ''}`;
                Telegram.WebApp.showAlert(message);
                Telegram.WebApp.HapticFeedback.impactOccurred('heavy');
            }
        });
    }
    
    // Ad refresh
    refreshAd() {
        if (this.adBlockDetected) return;
        this.loadAd();
    }
    
    // Performance tracking
    trackImpression(platform, adType) {
        fetch('/ad-impression', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                platform: platform,
                ad_type: adType,
                country: this.country
            })
        });
    }
}

// Initialize AdManager for global access
window.AdManager = AdManager;