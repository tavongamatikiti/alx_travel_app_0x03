# Security Best Practices

## ⚠️ CRITICAL: Environment Variables Security

### ❌ **NEVER Do This:**

```bash
# DON'T commit .env with real credentials to GitHub!
git add .env  # ❌ WRONG!
git commit -m "Add env file"  # ❌ DANGEROUS!
git push  # ❌ Your secrets are now public!
```

### ✅ **Always Do This:**

1. **Keep `.env` in `.gitignore`** (already done ✅)
2. **Only commit `.env.example`** with placeholder values
3. **Create `.env` directly on the server** with real credentials

---

## 🔐 Proper Workflow

### On Your Local Machine:

```bash
# 1. .env is already in .gitignore ✅
cat .gitignore | grep .env

# 2. Only commit .env.example (with fake values)
git add .env.example
git commit -m "Add environment variables template"
git push
```

### On PythonAnywhere (Production):

```bash
# 1. Upload code WITHOUT .env file
git clone https://github.com/YOUR_USERNAME/alx_travel_app_0x03.git
cd alx_travel_app_0x03

# 2. Create .env file DIRECTLY on the server
nano .env

# 3. Add your REAL credentials
# (This file never goes to GitHub - stays only on server)

# 4. Set proper permissions
chmod 600 .env  # Only you can read/write
```

---

## 📋 Environment Variables Checklist

### What Goes in GitHub:

✅ `.env.example` - Template with placeholders
```bash
# .env.example
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CELERY_BROKER_URL=amqp://user:pass@host/vhost
```

### What Stays on Server Only:

🔒 `.env` - Real credentials (NEVER commit!)
```bash
# .env (ON SERVER ONLY - NOT IN GITHUB)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
CELERY_BROKER_URL=amqp://username:password@cloudamqp.com/vhost
```

---

## 🛡️ PythonAnywhere Security

### How PythonAnywhere Handles Environment Variables:

**Method 1: .env File (Recommended)**
- Create `.env` file directly on PythonAnywhere via Files tab or Bash console
- File lives on their secure server
- Not accessible to public
- Not in version control

**Method 2: Web Interface (Paid Tiers Only)**
- Some platforms have environment variable settings in web UI
- PythonAnywhere free tier: use `.env` file instead

### Where to Store Credentials:

```
YOUR LOCAL MACHINE:
├── .env (with real keys - NOT committed)
├── .env.example (placeholders - committed ✅)
└── .gitignore (includes .env ✅)

GITHUB REPOSITORY:
├── .env.example (placeholders only ✅)
└── NO .env file ✅

PYTHONANYWHERE SERVER:
├── .env (with real keys - created on server)
└── NOT in version control ✅
```

---

## 🔑 Sensitive Information to Protect

Never commit these to GitHub:

- ❌ Gmail passwords or App Passwords
- ❌ Database passwords
- ❌ Django SECRET_KEY (production)
- ❌ API keys (Chapa, CloudAMQP, etc.)
- ❌ RabbitMQ credentials
- ❌ Any authentication tokens

---

## 🚨 What If You Accidentally Committed Secrets?

If you already pushed `.env` to GitHub:

### Emergency Steps:

1. **Immediately rotate ALL credentials**
   - Change Gmail App Password
   - Change database password
   - Generate new Django SECRET_KEY
   - Rotate all API keys

2. **Remove from Git history**
   ```bash
   # Remove .env from Git history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (if repo is not public yet)
   git push origin --force --all
   ```

3. **Add to .gitignore**
   ```bash
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "Add .env to gitignore"
   git push
   ```

4. **Better yet: Delete and recreate the repository**
   - Secrets in Git history are hard to fully remove
   - Safest: create new repo, don't commit .env

---

## ✅ Current Status of This Project

**Good news**: Your project is already secure! ✅

- `.env` is in `.gitignore` ✅
- Real credentials have been removed from `.env` ✅
- Only `.env.example` has placeholders ✅
- DEPLOYMENT.md has security warnings ✅

---

## 📖 Best Practices Summary

1. **Use `.env.example` for templates** (commit this)
2. **Use `.env` for real credentials** (NEVER commit)
3. **Keep `.env` in `.gitignore`** (already done)
4. **Create `.env` on server** (not in Git)
5. **Rotate secrets if exposed**
6. **Use strong, unique passwords**
7. **Enable 2FA where possible**

---

## 🔗 Additional Resources

- Django Security: https://docs.djangoproject.com/en/5.2/topics/security/
- GitHub Security: https://docs.github.com/en/code-security
- PythonAnywhere Security: https://help.pythonanywhere.com/pages/SecuringYourCode
- 12-Factor App (Environment Variables): https://12factor.net/config

---

## ✨ TL;DR

**Golden Rule**:
> `.env` with real secrets = NEVER in Git
> `.env.example` with fake values = Always in Git

**You're already following this!** ✅
