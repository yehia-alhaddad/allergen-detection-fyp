# Allergen Safety Checker - Web App

Production-ready Next.js web application for allergen detection and ingredient analysis.

## Features

- **Auth**: Secure sign-up/in with email + bcrypt password hashing, JWT sessions
- **Allergy Profile**: Personalized allergen list with synonyms + severity levels
- **Multi-method Detection**:
   - Image upload & camera capture → ML model inference
   - Ingredient text → direct analysis
- **Smart Matching**: Word-boundary aware, case-insensitive, supports "may contain" detection
- **Results**: Safe/Caution/Unsafe classification with matched allergen details + snippets
- **Accessibility**: Keyboard navigation, ARIA labels, high contrast

## Tech Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + TailwindCSS
- **Backend**: Next.js API routes + NextAuth for auth
- **Database**: Prisma ORM (SQLite dev, Postgres prod)
- **ML**: Call your FastAPI service; stub included

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up Environment

```bash
cp .env.example .env.local
# Edit .env.local: set NEXTAUTH_SECRET to a random 32+ char string
```

### 3. Initialize Database (SQLite for dev)

```bash
npx prisma migrate dev --name init
```

### 4. Run Locally

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000). Register, complete onboarding, and test!

## Production Deployment

### Use PostgreSQL

Update `.env.local`:
```
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql://user:password@host:5432/db
```

### Build & Run

```bash
npm run build
npm start
```

### Docker

```bash
docker build -t allergen-webapp .
docker run -p 3000:3000 -e DATABASE_URL=... allergen-webapp
```

## API Endpoints

- `POST /api/auth/register` - Create account
- `POST /api/auth/[...nextauth]` - NextAuth session
- `POST /api/profile/allergens` - Save/get allergens
- `POST /api/infer/image` - Multipart image → inference
- `POST /api/infer/capture` - Base64 camera frame → inference
- `POST /api/ingredients/check` - Text → ingredient analysis

## Connecting Your ML Model

Edit `lib/inference.ts`:

```typescript
export async function run_model_from_service(imageBase64: string): Promise<InferenceResult> {
  const url = process.env.ML_API_URL || 'http://localhost:8000/detect'
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageBase64 })
  })
  const data = await res.json()
  // Map your model's output to {labels: string[], confidences?: number[]}
  return { labels: data.labels, confidences: data.confidences }
}
```

Your model should return JSON with `{labels, confidences}` mapping detected allergens.

## File Structure

```
webapp/
├── app/
│   ├── (auth)/           # Auth pages (sign-in, sign-up)
│   ├── dashboard/        # Main entry
│   ├── onboarding/       # Setup allergen profile
│   ├── profile/          # View/edit allergens
│   ├── scan/             # Scan routes (upload, camera, text)
│   ├── api/              # API routes
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Landing page
├── components/
│   ├── scan/             # Scan UI (camera, result)
│   └── ui/               # Reusable UI components
├── lib/
│   ├── allergy.ts        # Allergen matching logic
│   ├── inference.ts      # ML model adapter
│   ├── rateLimiter.ts    # Simple token bucket
│   ├── auth.ts           # NextAuth config
│   ├── db.ts             # Prisma client
├── prisma/
│   └── schema.prisma     # DB schema
├── styles/
│   └── globals.css       # Tailwind + custom
└── public/               # Static assets
```

## Acceptance Tests

Run these to verify the app works:

1. **Landing Page**
   - Visit [http://localhost:3000](http://localhost:3000)
   - See title, description, "Start Scan" button
   - Click "Start Scan" → redirects to dashboard

2. **Sign Up**
   - Go to [http://localhost:3000/(auth)/sign-up](http://localhost:3000/(auth)/sign-up)
   - Fill name, email, password → click Sign up
   - Should redirect to onboarding

3. **Onboarding**
   - Select 2+ common allergens (e.g., milk, peanuts)
   - Click "Save profile"
   - Should redirect to dashboard

4. **Ingredient Text Check**
   - In dashboard, click "Paste Ingredients"
   - Paste: `Water, milk powder, salt, sugar`
   - Click Analyze
   - Should show: classification=UNSAFE, matched allergen="milk"

5. **Profile Page**
   - Sign in, go to [http://localhost:3000/profile](http://localhost:3000/profile)
   - Should list saved allergens

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_PROVIDER` | sqlite | `sqlite` or `postgresql` |
| `DATABASE_URL` | `file:./dev.db` | DB connection string |
| `NEXTAUTH_SECRET` | *required* | Min 32 random chars for JWT signing |
| `NEXTAUTH_URL` | `http://localhost:3000` | Your app URL |
| `ML_API_URL` | `http://localhost:8000/detect-text` | Your ML service endpoint |
| `NODE_ENV` | `development` | `development` or `production` |

## Notes

- **No medical claims**: Results are advisory. Always tell users to verify labels.
- **Rate limiting**: Simple in-memory token bucket. For production, use Redis/Memcached.
- **Images**: By default, only results are stored—not raw images. Toggle `storeRawImage` in ScanHistory for opt-in.
- **Camera**: Requires HTTPS in production; localhost works fine for dev.
- **Error handling**: All endpoints return JSON with status codes. Frontend provides user feedback.

## Next Steps

- [ ] Connect your ML model endpoint in `lib/inference.ts`
- [ ] Test with real product images
- [ ] Configure Postgres for production
- [ ] Set secure `NEXTAUTH_SECRET`
- [ ] Deploy to Vercel, Heroku, or your infrastructure
- [ ] Consider adding email verification, password reset, audit logs
