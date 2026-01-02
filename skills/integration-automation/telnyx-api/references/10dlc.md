# 10DLC (10-Digit Long Code) Reference

## What is 10DLC?

10DLC is a registration system for Application-to-Person (A2P) messaging in the United States. All US businesses sending SMS via local 10-digit phone numbers must register their brand and messaging campaigns with The Campaign Registry (TCR) for carrier approval.

**Why it exists:**
- Reduce spam and improve message deliverability
- Give carriers visibility into business messaging
- Ensure compliance with TCPA and CTIA guidelines
- Set appropriate throughput limits based on use case

**Cost Impact:**
- **Unregistered**: ~$0.0141/message (2x cost, poor delivery)
- **Registered 10DLC**: ~$0.0079/message (approved rate, excellent delivery)
- **Toll-free**: ~$0.0095/message (requires RespOrg verification, 2-4 weeks)

## Campaign Approval Stages (CRITICAL)

Your campaign goes through **three distinct approval stages**. Understanding these is crucial:

### Stage 1: TCR_ACCEPTED ✅
**What it means:** The Campaign Registry (TCR) has approved your campaign registration.
**Can you send messages?** No - carriers haven't provisioned yet.
**Can you associate phone numbers?** No - must wait for MNO_PROVISIONED.
**Timeline:** Immediate after submission (if all fields valid).

**Example Status:**
```json
{
  "campaignStatus": "TCR_ACCEPTED",
  "status": "ACTIVE",
  "tcrCampaignId": "C55K5WI"
}
```

### Stage 2: MNO_PENDING ⏳
**What it means:** Waiting for Mobile Network Operator (carrier) approval.
**Can you send messages?** No - carriers are still reviewing.
**Can you associate phone numbers?** No - still waiting.
**Timeline:** 1-3 business days after TCR_ACCEPTED.

**What's happening:**
- AT&T reviewing campaign
- Verizon reviewing campaign
- T-Mobile reviewing campaign
- Each carrier independently approves

**Example Status:**
```json
{
  "campaignStatus": "MNO_PENDING",
  "status": "ACTIVE",
  "isTMobileRegistered": false
}
```

### Stage 3: MNO_PROVISIONED 🎯
**What it means:** All carriers have approved and provisioned your campaign.
**Can you send messages?** Yes - full carrier approval, optimal delivery.
**Can you associate phone numbers?** Yes - ready for production.
**Timeline:** You've arrived! Start sending.

**Example Status:**
```json
{
  "campaignStatus": "MNO_PROVISIONED",
  "status": "ACTIVE",
  "isTMobileRegistered": true
}
```

**Action required:**
1. Associate your phone number(s) with the campaign
2. Test message delivery
3. Monitor delivery rates for first 24 hours

## Registration Process

### Step 1: Register Your Brand (Brand Verification)
First, register your business/organization as a brand with The Campaign Registry (TCR). This step verifies your business identity to carriers.

**Required Information:**
- **Legal business name** - Must match official registration documents
- **Business type** - Corporation, LLC, Partnership, Non-profit, Sole Proprietor, etc.
- **EIN (Tax ID)** - Federal Employer Identification Number (required for verification)
- **Business address** - Physical address (not P.O. Box)
- **Website URL** - Active, publicly accessible website
- **Business vertical** - Industry category (Healthcare, Education, Technology, etc.)
- **Contact information** - Primary business phone and email
- **Business registration state** - State where business is registered

**Data Accuracy Critical:** All information must match official business records. Inconsistencies (e.g., business name mismatch between EIN and website) will delay or reject approval.

**Timeline:** 2-3 business days for verification and approval

**Verification Process:**
1. TCR validates business information against official databases
2. Checks EIN against IRS records
3. Verifies business website is active and matches business name
4. Assigns trust score based on business age, type, and reputation
5. Approves or requests additional documentation

**API Check Brand Status:**
```bash
curl -s https://api.telnyx.com/v2/10dlc/brand/{brandId} \
  -H "Authorization: Bearer YOUR_API_KEY" \
  | jq '.brandStatus'
```

### Step 2: Create Campaign (Campaign Vetting)
After brand approval, create a messaging campaign. **As of January 2023, all campaigns undergo manual vetting** by The Campaign Registry.

**Required Information:**
- **Campaign description** (max 500 chars) - Clear, specific description of messaging purpose
- **Use case** - Customer Care, Marketing, 2FA, Account Notifications, etc.
- **Sample messages** (3-5 examples) - Must be representative of actual messages you'll send
- **Opt-in workflow description** - How users consent to receive messages (must be verifiable)
- **Opt-out process** - How users can unsubscribe (STOP keyword minimum)
- **Help message** - Response to HELP keyword
- **Privacy policy URL** - Must be publicly accessible
- **Terms & conditions URL** - Must be publicly accessible
- **User consent method** - Web form, verbal, paper signup, etc.
- **Age-gating** (if applicable) - 18+, 21+ requirements
- **Embedded links/phone numbers** - Declare if messages contain URLs or phone numbers

**Manual Vetting Requirements (Critical):**
- **User Consent (Call to Action)** must be accessible by reviewers for verification
- If opt-in is behind a login, provide screenshots and explanation
- All URLs (privacy policy, terms) must be live and functional
- Sample messages must match actual message content
- Campaign description must accurately reflect messaging purpose
- **Do NOT include PII** (Personal Identifiable Information) in registration fields

**Timeline:**
- TCR submission: 5-10 minutes
- TCR manual review: 1-3 business days (TCR_ACCEPTED)
- MNO provisioning: 1-3 business days (MNO_PROVISIONED)
- **Total**: 3-5 business days from submission to full approval

**API Check Campaign Status:**
```bash
curl -s https://api.telnyx.com/v2/10dlc/campaign/{campaignId} \
  -H "Authorization: Bearer YOUR_API_KEY" \
  | jq '.campaignStatus'
```

### Step 3: Associate Phone Numbers
**ONLY after status = MNO_PROVISIONED**

Associate your 10-digit phone numbers with the approved campaign. This is done in the Telnyx portal:

1. Navigate to **Messaging → 10DLC → Campaigns**
2. Click on your approved campaign
3. Go to **Phone Numbers** or **Associated Numbers** section
4. Click **Add Number** and select your number(s)

**Why manual?** Campaign-to-number association is not exposed via the Telnyx API as of 2025.

## Monitoring Campaign Status

### Check Status via API
```bash
#!/bin/bash
# monitor-campaign.sh

CAMPAIGN_ID="your-campaign-id"
API_KEY="your-api-key"

while true; do
  STATUS=$(curl -s "https://api.telnyx.com/v2/10dlc/campaign/${CAMPAIGN_ID}" \
    -H "Authorization: Bearer ${API_KEY}" \
    | jq -r '.campaignStatus')

  echo "$(date): Campaign status = ${STATUS}"

  if [ "$STATUS" = "MNO_PROVISIONED" ]; then
    echo "✅ Campaign fully approved! Ready to associate phone numbers."
    exit 0
  fi

  sleep 300  # Check every 5 minutes
done
```

### Key Status Fields
```json
{
  "campaignStatus": "MNO_PROVISIONED",      // Main approval status
  "status": "ACTIVE",                        // Campaign active state
  "isTMobileRegistered": true,              // T-Mobile approval
  "isTMobileSuspended": false,              // T-Mobile suspension status
  "failureReasons": null,                   // Rejection reasons (if any)
  "brandDisplayName": "Your Company"
}
```

## Use Cases

### Customer Care (Recommended for Support Services)
**Description:** Two-way conversations for support, service, and account management.

**Examples:**
- Customer support inquiries
- Order status updates
- Appointment reminders with reply options
- Service issue resolution

**Approval:** Generally fastest approval (1-3 days)
**Throughput:** Higher limits than marketing

### Marketing
**Description:** Promotional content, offers, and advertising.

**Examples:**
- Sales promotions
- New product announcements
- Limited-time offers
- Event invitations

**Approval:** May require additional vetting (3-5 days)
**Throughput:** Lower limits than customer care
**Requirements:** Must honor opt-out within 24 hours

### 2FA (Two-Factor Authentication)
**Description:** One-time passwords and authentication codes.

**Examples:**
- Login verification codes
- Password reset codes
- Transaction confirmations

**Approval:** Fast approval (1-2 days)
**Throughput:** Highest limits (security priority)

### Account Notifications
**Description:** Transactional updates about user accounts.

**Examples:**
- Payment confirmations
- Shipping notifications
- Account balance alerts
- Security alerts

**Approval:** Fast approval (1-2 days)
**Throughput:** High limits

## Compliance Requirements

### TCPA (Telephone Consumer Protection Act)
- ✅ Prior express written consent required
- ✅ Clear opt-out mechanism (STOP keyword)
- ✅ Sender identification in messages
- ✅ Honor opt-outs within 24 hours

### CTIA Best Practices
- ✅ Include "Message and data rates may apply"
- ✅ Include message frequency disclosure
- ✅ Provide HELP keyword with support info
- ✅ Age-gate if content requires (18+, 21+)
- ✅ No sharing/selling of phone numbers

### Required Message Elements

**Opt-In Confirmation (first message after signup):**
```
Welcome! You've successfully subscribed to [Service Name].
Reply STOP to unsubscribe, HELP for assistance.
Msg&data rates may apply.
```

**Opt-Out Confirmation (after STOP keyword):**
```
You've been unsubscribed from [Service Name].
You won't receive further messages.
```

**HELP Response:**
```
[Service Name] - [Brief description].
Reply STOP to unsubscribe.
Support: [phone/email/URL]
```

## Common Issues and Solutions

### Issue: Campaign Stuck in MNO_PENDING for >5 Days
**Cause:** Carriers may be waiting for additional information.
**Solution:**
- Check `failureReasons` field in API response
- Contact Telnyx support: 10dlcquestions@telnyx.com
- Provide campaign ID and TCR brand ID

### Issue: Cannot Associate Phone Number
**Cause:** Campaign status is not MNO_PROVISIONED yet.
**Solution:** Wait for full carrier approval. Check status with:
```bash
curl -s https://api.telnyx.com/v2/10dlc/campaign/{id} \
  -H "Authorization: Bearer ${API_KEY}" | jq '.campaignStatus'
```

### Issue: Messages Not Delivering After Association
**Cause:** Carrier filters, content issues, or number not properly linked.
**Solution:**
1. Verify number shows in campaign's associated numbers
2. Check message content for spam triggers (all caps, excessive links)
3. Test with a simple "Hello" message first
4. Check webhook for delivery status

### Issue: Campaign Rejected
**Cause:** Non-compliant description, missing required fields, or prohibited content.
**Solution:**
- Review `failureReasons` in API response
- Common fixes:
  - Add opt-in workflow description
  - Include all required sample messages (3-5)
  - Ensure privacy policy and T&C URLs are live
  - Remove prohibited content (cannabis, debt collection, etc.)

## API Reference

### Get Campaign Status
```bash
GET /v2/10dlc/campaign/{campaignId}
```

**Response:**
```json
{
  "campaignId": "4b30019a-16f6-82ef-d3e3-3ab7dcba2345",
  "campaignStatus": "MNO_PROVISIONED",
  "status": "ACTIVE",
  "tcrCampaignId": "C55K5WI",
  "tcrBrandId": "BY9LCV1",
  "usecase": "CUSTOMER_CARE",
  "description": "Your campaign description...",
  "createDate": "2025-10-24T16:04:06.000Z",
  "nextRenewalOrExpirationDate": "2026-01-24",
  "isTMobileRegistered": true,
  "isTMobileSuspended": false,
  "failureReasons": null
}
```

### Get Brand Status
```bash
GET /v2/10dlc/brand/{brandId}
```

**Response:**
```json
{
  "brandId": "4b20019a-1692-7815-832f-5cf2644b6691",
  "brandStatus": "APPROVED",
  "tcrBrandId": "BY9LCV1",
  "displayName": "Aldea AI",
  "companyName": "Aldea AI Inc",
  "ein": "XX-XXXXXXX",
  "vertical": "PROFESSIONAL"
}
```

### Note on Phone Number Association
**Campaign-to-number association is NOT available via API.**

The Telnyx API phone numbers endpoint (`PATCH /v2/phone_numbers/{id}`) does not accept `messaging_campaign_id` as a parameter. You must use the Telnyx portal to associate numbers with campaigns.

**Attempted API call (does not work):**
```bash
# This will NOT associate the campaign
curl -X PATCH "https://api.telnyx.com/v2/phone_numbers/+1234567890" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"messaging_campaign_id": "campaign-id"}'

# Response will show messaging_campaign_id: null
```

**Correct approach:** Use Telnyx portal → Messaging → 10DLC → Campaigns → [Your Campaign] → Phone Numbers

## Cost Structure

### Monthly Fees
- **Brand registration:** Free
- **Campaign fee:** $10/month per campaign
- **Phone number:** ~$1-2.50/month depending on type

### Per-Message Costs (after 10DLC approval)
- **Customer Care:** ~$0.0079/segment
- **Marketing:** ~$0.0095/segment
- **2FA:** ~$0.0055/segment
- **Unregistered:** ~$0.0141/segment (2x penalty)

### Message Segmentation
- **GSM-7 encoding:** 160 chars = 1 segment
- **UCS-2 (emoji/unicode):** 70 chars = 1 segment
- **Multi-part GSM-7:** 153 chars per segment
- **Multi-part UCS-2:** 67 chars per segment

**Cost optimization tip:** Avoid emoji/unicode to use GSM-7 encoding and reduce costs by ~2x.

## Timeline Summary

| Stage | Duration | What Happens |
|-------|----------|--------------|
| Brand Registration | 24-48 hours | TCR verifies business info |
| Campaign Submission | 5-10 minutes | Fill out campaign form |
| TCR Approval | Minutes to hours | Campaign Registry approves |
| MNO Provisioning | 1-3 business days | AT&T, Verizon, T-Mobile approve |
| Number Association | 5 minutes | Manual portal step |
| **Total Time** | **3-5 business days** | From brand submission to sending |

## Production Checklist

Before going live with 10DLC:

- [ ] Brand registered and approved (status = APPROVED)
- [ ] Campaign created with accurate description
- [ ] All 3-5 sample messages representative of actual usage
- [ ] Opt-in workflow documented and implemented
- [ ] Opt-out handler responds to STOP keyword
- [ ] HELP keyword returns informative message
- [ ] Privacy policy URL is live and accessible
- [ ] Terms & conditions URL is live and accessible
- [ ] Campaign status = MNO_PROVISIONED (not just TCR_ACCEPTED)
- [ ] Phone number(s) associated with campaign in portal
- [ ] Test message sent successfully
- [ ] Webhook configured to track delivery status
- [ ] Monitoring set up for delivery rates
- [ ] Budget allocated for monthly campaign fee ($10/month)

## Support Resources

- **Telnyx 10DLC Support:** 10dlcquestions@telnyx.com
- **Telnyx Status Page:** https://status.telnyx.com/
- **TCR (The Campaign Registry):** https://www.campaignregistry.com/
- **CTIA Guidelines:** https://www.ctia.org/the-wireless-industry/industry-commitments/messaging-principles-and-best-practices
