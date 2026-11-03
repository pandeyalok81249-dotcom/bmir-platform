# Google Play Store Data Safety & Production Release Checklist

## 1. Application Identification
- **App Name**: AI Resume Intelligence & Career Platform
- **Application ID / Package Name**: `com.antigravity.resumeintelligence`
- **Target SDK**: Android 14 (API level 34)
- **Minimum SDK**: Android 7.0 (API level 24)
- **Category**: Productivity / Business / Career

---

## 2. Google Play Console Data Safety Form Declaration

| Category | Data Type | Collected? | Shared? | Purpose | Ephemeral / Stored | Can User Delete? |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| **Personal Info** | Name | YES | NO | Account management, profile personalization | Stored until account deletion | YES |
| **Personal Info** | Email address | YES | NO | Authentication, password reset, notifications | Stored until account deletion | YES |
| **Financial Info** | Purchase history | YES | NO | Subscription entitlement verification | Stored for tax & accounting | YES (anonymized) |
| **Files & Docs** | Resumes, career text | YES | NO | Resume audit, evidence graph, job matching | Stored in private bucket | YES |
| **App Activity** | Feature interactions | YES | NO | Quota enforcement, product analytics | Stored in pseudonymized form | YES |
| **Device IDs** | IP address, OS version | YES | NO | Fraud prevention, rate limiting, diagnostics | Ephemeral (sliding window) | N/A |

### Security Practices Declared:
- [x] **Data encrypted in transit**: All network traffic is encrypted via HTTPS / TLS 1.3.
- [x] **Data deletion request supported**: Users can request complete account and data deletion in-app or via web URL.
- [x] **Committed to Play Families Policy**: Target audience is 18+.

---

## 3. Production Release Build & Signing Checklist
1. **Keystore Generation**:
   ```bash
   keytool -genkey -v -keystore android/upload-keystore.jks -alias upload -keyalg RSA -keysize 2048 -validity 10000
   ```
2. **Key Properties Configuration**:
   Create `android/key.properties`:
   ```properties
   storePassword=<PASSWORD>
   keyPassword=<PASSWORD>
   keyAlias=upload
   storeFile=../upload-keystore.jks
   ```
3. **ProGuard / R8 Verification**:
   Verify `android/app/proguard-rules.pro` preserves model serialization and reflection where necessary.
4. **App Bundle Compilation**:
   ```bash
   flutter build appbundle --release
   ```
5. **AAB Output Validation**:
   Inspect generated bundle at `build/app/outputs/bundle/release/app-release.aab` with `bundletool` before uploading to Play Console Internal Testing track.

