import express from "express";
import { createServer as createViteServer } from "vite";
import mongoose from "mongoose";
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017/stylemate";
mongoose.connect(MONGODB_URI)
  .then(() => console.log("Connected to MongoDB"))
  .catch(err => console.error("MongoDB connection error:", err));

// User Schema
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  name: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model("User", userSchema);

// Recommendation Logic (Ported from Python)
const bodyShapes = ['apple', 'hourglass', 'inverted_triangle', 'pear', 'rectangle'];
const skinClasses = ["dark", "light", "mid-dark", "mid-light"];

const recommendations: any = {
    'apple': {
        'dark': {
            'casual': "White top color, A-line fit type, cotton fabric, solid or vertical stripe pattern. Opt for a white A-line cotton dress with solid pattern to skim over the midsection, paired with wide-leg pants and flats for balance and comfort. This enhances your legs and creates a streamlined silhouette.",
            'formal': "Yellow top color, empire waist fit type, silk fabric, solid pattern. Choose a yellow empire waist silk dress with solid pattern to draw attention upward, with structured shoulders and heels for an elegant, lengthening effect.",
            'party': "Bright pink top color, wrap fit type, chiffon fabric, subtle vertical pattern. Wear a bright pink wrap chiffon dress with subtle vertical patterns, accessorized with shiny jewelry to flatter your figure and add glamour."
        },
        'mid-dark': {
            'casual': "Red top color, A-line fit type, linen fabric, solid pattern. Select a red A-line linen dress with solid pattern, combined with bootcut jeans and flats to elongate the torso and highlight your best features.",
            'formal': "Cream top color, empire waist fit type, satin fabric, vertical seam pattern. Go for a cream empire waist satin dress with vertical seams for a flattering formal look, paired with heels to create shape without clinging.",
            'party': "Orange top color, wrap fit type, velvet fabric, solid pattern. Embrace an orange wrap velvet dress with solid pattern and shiny accessories to celebrate your silhouette at parties."
        },
        'mid-light': {
            'casual': "Blue top color, A-line fit type, cotton fabric, vertical stripe pattern. A blue A-line cotton dress with vertical stripes, worn with wide-leg trousers and flats, provides a relaxed yet flattering casual outfit.",
            'formal': "Green top color, empire waist fit type, wool fabric, solid pattern. Choose a green empire waist wool dress with solid pattern for formal occasions, adding heels for sophistication.",
            'party': "Lavender top color, wrap fit type, chiffon fabric, subtle pattern. Opt for a lavender wrap chiffon dress with subtle patterns and shiny accessories to enhance your party presence."
        },
        'light': {
            'casual': "Black top color, A-line fit type, denim fabric, solid pattern. Wear a black A-line denim dress with solid pattern, paired with flats for a chic casual look that balances proportions.",
            'formal': "Navy top color, empire waist fit type, silk fabric, vertical pattern. A navy empire waist silk dress with vertical patterns offers a polished formal appearance with heels.",
            'party': "Maroon top color, wrap fit type, sequin fabric, solid pattern. Select a maroon wrap sequin dress with solid pattern and shiny accessories for a stunning party outfit."
        }
    },
    'hourglass': {
        'dark': {
            'casual': "White top color, wrap fit type, cotton fabric, solid pattern. A white wrap cotton dress with solid pattern and flats accentuates your curves perfectly for casual wear.",
            'formal': "Yellow top color, bodycon fit type, silk fabric, subtle pattern. Choose a yellow bodycon silk dress with subtle patterns and heels to highlight your silhouette in formal settings.",
            'party': "Bright pink top color, belted fit type, chiffon fabric, solid pattern. Wear a bright pink belted chiffon dress with solid pattern and shiny accessories for party elegance."
        },
        'mid-dark': {
            'casual': "Red top color, wrap fit type, linen fabric, solid pattern. Opt for a red wrap linen dress with solid pattern, paired with flats to embrace your natural shape casually.",
            'formal': "Cream top color, bodycon fit type, satin fabric, subtle pattern. A cream bodycon satin dress with subtle patterns and heels provides a sophisticated formal look.",
            'party': "Orange top color, belted fit type, velvet fabric, solid pattern. Select an orange belted velvet dress with solid pattern and shiny accessories for vibrant party style."
        },
        'mid-light': {
            'casual': "Blue top color, wrap fit type, cotton fabric, solid pattern. A blue wrap cotton dress with solid pattern and flats flatters your proportions in casual outfits.",
            'formal': "Green top color, bodycon fit type, wool fabric, subtle pattern. Choose a green bodycon wool dress with subtle patterns and heels for formal occasions.",
            'party': "Lavender top color, belted fit type, chiffon fabric, solid pattern. Wear a lavender belted chiffon dress with solid pattern and shiny accessories to shine at parties."
        },
        'light': {
            'casual': "Black top color, wrap fit type, denim fabric, solid pattern. Opt for a black wrap denim dress with solid pattern and flats for a balanced casual appearance.",
            'formal': "Navy top color, bodycon fit type, silk fabric, subtle pattern. A navy bodycon silk dress with subtle patterns and heels enhances your figure formally.",
            'party': "Maroon top color, belted fit type, sequin fabric, solid pattern. Select a maroon belted sequin dress with solid pattern and shiny accessories for party glamour."
        }
    },
    'inverted_triangle': {
        'dark': {
            'casual': "White top color, V-neck fit type, cotton fabric, vertical stripe pattern. A white V-neck cotton top with vertical stripes, paired with flared pants and flats, adds balance casually.",
            'formal': "Yellow top color, A-line fit type, silk fabric, small print pattern. Choose a yellow A-line silk dress with small prints and heels to create harmony in formal attire.",
            'party': "Bright pink top color, off-shoulder fit type, chiffon fabric, solid pattern. Wear a bright pink off-shoulder chiffon dress with solid pattern and shiny accessories for party flair."
        },
        'mid-dark': {
            'casual': "Red top color, V-neck fit type, linen fabric, vertical pattern. Opt for a red V-neck linen top with vertical patterns, flared pants, and flats for casual balance.",
            'formal': "Cream top color, A-line fit type, satin fabric, small print pattern. A cream A-line satin dress with small prints and heels softens shoulders formally.",
            'party': "Orange top color, off-shoulder fit type, velvet fabric, solid pattern. Select an orange off-shoulder velvet dress with solid pattern and shiny accessories."
        },
        'mid-light': {
            'casual': "Blue top color, V-neck fit type, cotton fabric, vertical stripe pattern. A blue V-neck cotton top with vertical stripes, flared pants, and flats enhances lower body casually.",
            'formal': "Green top color, A-line fit type, wool fabric, small print pattern. Choose a green A-line wool dress with small prints and heels for formal proportion.",
            'party': "Lavender top color, off-shoulder fit type, chiffon fabric, solid pattern. Wear a lavender off-shoulder chiffon dress with solid pattern and shiny accessories."
        },
        'light': {
            'casual': "Black top color, V-neck fit type, denim fabric, vertical pattern. Opt for a black V-neck denim top with vertical patterns, flared pants, and flats.",
            'formal': "Navy top color, A-line fit type, silk fabric, small print pattern. A navy A-line silk dress with small prints and heels creates balance formally.",
            'party': "Maroon top color, off-shoulder fit type, sequin fabric, solid pattern. Select a maroon off-shoulder sequin dress with solid pattern and shiny accessories."
        }
    },
    'pear': {
        'dark': {
            'casual': "White top color, off-shoulder fit type, cotton fabric, horizontal stripe pattern. A white off-shoulder cotton top with horizontal stripes + A-line skirt and flats draws attention upward.",
            'formal': "Yellow top color, V-neck fit type, silk fabric, bold pattern on top. Choose a yellow V-neck silk top with bold patterns + flared pants and heels for formal balance.",
            'party': "Bright pink top color, fit-and-flare fit type, chiffon fabric, solid pattern. Wear a bright pink fit-and-flare chiffon dress with solid pattern and shiny accessories."
        },
        'mid-dark': {
            'casual': "Red top color, off-shoulder fit type, linen fabric, horizontal pattern. Opt for a red off-shoulder linen top with horizontal patterns + A-line skirt and flats.",
            'formal': "Cream top color, V-neck fit type, satin fabric, bold pattern. A cream V-neck satin top with bold patterns + flared pants and heels enhances upper body.",
            'party': "Orange top color, fit-and-flare fit type, velvet fabric, solid pattern. Select an orange fit-and-flare velvet dress with solid pattern and shiny accessories."
        },
        'mid-light': {
            'casual': "Blue top color, off-shoulder fit type, cotton fabric, horizontal stripe pattern. A blue off-shoulder cotton top with horizontal stripes + A-line skirt and flats flatters proportions.",
            'formal': "Green top color, V-neck fit type, wool fabric, bold pattern. Choose a green V-neck wool top with bold patterns + flared pants and heels.",
            'party': "Lavender top color, fit-and-flare fit type, chiffon fabric, solid pattern. Wear a lavender fit-and-flare chiffon dress with solid pattern and shiny accessories."
        },
        'light': {
            'casual': "Black top color, off-shoulder fit type, denim fabric, horizontal pattern. Opt for a black off-shoulder denim top with horizontal patterns + A-line skirt and flats.",
            'formal': "Navy top color, V-neck fit type, silk fabric, bold pattern. A navy V-neck silk top with bold patterns + flared pants and heels for formal style.",
            'party': "Maroon top color, fit-and-flare fit type, sequin fabric, solid pattern. Select a maroon fit-and-flare sequin dress with solid pattern and shiny accessories."
        }
    },
    'rectangle': {
        'dark': {
            'casual': "White top color, peplum fit type, cotton fabric, bold print pattern. A white peplum cotton top with bold prints + jeans and flats creates curves casually.",
            'formal': "Yellow top color, belted fit type, silk fabric, horizontal stripe pattern. Choose a yellow belted silk dress with horizontal stripes and heels for formal definition.",
            'party': "Bright pink top color, ruffled fit type, chiffon fabric, floral pattern. Wear a bright pink ruffled chiffon dress with floral patterns and shiny accessories."
        },
        'mid-dark': {
            'casual': "Red top color, peplum fit type, linen fabric, bold pattern. Opt for a red peplum linen top with bold patterns + jeans and flats.",
            'formal': "Cream top color, belted fit type, satin fabric, horizontal pattern. A cream belted satin dress with horizontal patterns and heels adds shape formally.",
            'party': "Orange top color, ruffled fit type, velvet fabric, polka dot pattern. Select an orange ruffled velvet dress with polka dots and shiny accessories."
        },
        'mid-light': {
            'casual': "Blue top color, peplum fit type, cotton fabric, bold print pattern. A blue peplum cotton top with bold prints + jeans and flats enhances curves.",
            'formal': "Green top color, belted fit type, wool fabric, horizontal stripe pattern. Choose a green belted wool dress with horizontal stripes and heels.",
            'party': "Lavender top color, ruffled fit type, chiffon fabric, floral pattern. Wear a lavender ruffled chiffon dress with floral patterns and shiny accessories."
        },
        'light': {
            'casual': "Black top color, peplum fit type, denim fabric, bold pattern. Opt for a black peplum denim top with bold patterns + jeans and flats.",
            'formal': "Navy top color, belted fit type, silk fabric, horizontal pattern. A navy belted silk dress with horizontal patterns and heels for formal elegance.",
            'party': "Maroon top color, ruffled fit type, sequin fabric, leopard print pattern. Select a maroon ruffled sequin dress with leopard prints and shiny accessories."
        }
    }
};

const explanations: any = {
    'apple': {
        'dark': {
            'casual': "For apple body shapes, A-line fits skim over the midsection to create balance and elongate the silhouette, avoiding emphasis on the waist. White contrasts vibrantly with dark skin tones, enhancing overall brightness. In casual settings, cotton provides breathability and comfort, while vertical stripes add height and slimness.",
            'formal': "Empire waist fits for apple shapes draw the eye upward and away from the midsection, creating a lengthening effect with structure. Yellow pops against dark skin, adding warmth and elegance. Silk fabric in formal wear offers a luxurious drape that flatters without clinging.",
            'party': "Wrap fits accentuate the bust and legs for apple shapes while camouflaging the midsection. Bright pink provides a bold, flattering contrast on dark skin. Chiffon adds flow and glamour for parties, with vertical patterns subtly elongating the figure."
        },
        'mid-dark': {
            'casual': "A-line styles balance apple proportions by flowing over the midsection and highlighting legs. Red warms mid-dark skin tones, creating a lively look. Linen is ideal for casual comfort with its breathable nature, and solid patterns keep it simple yet effective.",
            'formal': "For apple shapes, empire waist creates definition without tightness, paired with vertical seams for illusion of length. Cream softens mid-dark skin for sophistication. Satin's sheen adds formal polish and smooth flow.",
            'party': "Wrap designs for apple bodies tie at the slimmest point, enhancing curves tastefully. Orange energizes mid-dark skin. Velvet provides rich texture for party wear, with solids allowing accessories to shine."
        },
        'mid-light': {
            'casual': "A-line fits help apple shapes achieve a streamlined look by not hugging the waist. Blue cools and complements mid-light skin. Cotton ensures casual ease, and vertical stripes visually elongate the torso.",
            'formal': "Empire waist in apple-friendly designs raises the waistline for better proportions. Green harmonizes with mid-light skin for a fresh vibe. Wool offers structured formality without bulk.",
            'party': "Wrap styles flatter apple figures by creating shape and movement. Lavender soothes mid-light skin tones. Chiffon brings airy elegance to parties, with subtle patterns adding interest without overwhelming."
        },
        'light': {
            'casual': "For apple bodies, A-line provides balance by widening at the bottom. Black deepens light skin for contrast. Denim's durability suits casual lifestyles, with solids for versatility.",
            'formal': "Empire waist elevates focus for apple shapes, aided by vertical patterns for slimming. Navy anchors light skin elegantly. Silk drapes smoothly for formal refinement.",
            'party': "Wrap fits define the figure for apple shapes without constriction. Maroon enriches light skin. Sequin adds sparkle for parties, solids keeping focus on shine."
        }
    },
    'hourglass': {
        'dark': {
            'casual': "Wrap fits accentuate the defined waist of hourglass shapes naturally. White brightens dark skin dramatically. Cotton keeps casual outfits comfortable, solids for clean lines.",
            'formal': "Bodycon hugs hourglass curves precisely for a flattering silhouette. Yellow vibrates against dark skin. Silk enhances formal smoothness and sheen.",
            'party': "Belted styles emphasize the waist in hourglass figures. Bright pink contrasts boldly on dark skin. Chiffon flows gracefully for party movement."
        },
        'mid-dark': {
            'casual': "Wrap designs follow hourglass contours for effortless flattery. Red warms mid-dark skin. Linen offers casual breathability, solids for simplicity.",
            'formal': "Bodycon fits showcase hourglass balance. Cream softens mid-dark tones elegantly. Satin provides formal luster.",
            'party': "Belted fits highlight the natural waist of hourglass shapes. Orange energizes mid-dark skin. Velvet adds plush party texture."
        },
        'mid-light': {
            'casual': "Wrap styles cinch at the waist for hourglass enhancement. Blue complements mid-light skin coolly. Cotton ensures casual comfort.",
            'formal': "Bodycon embraces hourglass proportions. Green refreshes mid-light skin. Wool structures formal looks durably.",
            'party': "Belted designs define hourglass curves. Lavender calms mid-light tones. Chiffon brings light party flow."
        },
        'light': {
            'casual': "Wrap fits flatter hourglass by wrapping around curves. Black deepens light skin. Denim suits casual ruggedness.",
            'formal': "Bodycon highlights hourglass symmetry. Navy grounds light skin sophisticatedly. Silk drapes formally.",
            'party': "Belted styles accent hourglass waists. Maroon enriches light skin. Sequin sparkles for parties."
        }
    },
    'inverted_triangle': {
        'dark': {
            'casual': "V-neck narrows broad shoulders in inverted triangle shapes, with vertical stripes slimming upper body. White contrasts dark skin. Cotton comforts casually, flared bottoms balance.",
            'formal': "A-line widens at hips for inverted triangle balance. Yellow brightens dark skin. Silk polishes formal looks, small prints distract from shoulders.",
            'party': "Off-shoulder softens inverted triangle shoulders. Bright pink pops on dark skin. Chiffon adds party softness."
        },
        'mid-dark': {
            'casual': "V-neck minimizes shoulder width for inverted triangles, vertical patterns elongate. Red warms mid-dark skin. Linen breathes casually.",
            'formal': "A-line creates lower body volume for inverted triangle balance. Cream elegant on mid-dark. Satin shines formally.",
            'party': "Off-shoulder exposes for softness in inverted triangles. Orange vibrant on mid-dark. Velvet textures party wear."
        },
        'mid-light': {
            'casual': "V-neck slims upper body for inverted triangles, vertical stripes aid. Blue cools mid-light skin. Cotton casual ease.",
            'formal': "A-line balances inverted triangle proportions. Green fresh on mid-light. Wool structures formally.",
            'party': "Off-shoulder flatters inverted triangles by softening lines. Lavender soothes mid-light. Chiffon flows for parties."
        },
        'light': {
            'casual': "V-neck reduces shoulder emphasis in inverted triangles. Black contrasts light skin. Denim durable casually.",
            'formal': "A-line adds hip volume for inverted triangles. Navy sophisticated on light. Silk drapes formally.",
            'party': "Off-shoulder gentles inverted triangle shoulders. Maroon deepens light skin. Sequin glimmers for parties."
        }
    },
    'pear': {
        'dark': {
            'casual': "Off-shoulder draws eyes up for pear shapes, horizontal stripes widen top. White brightens dark skin. Cotton comfortable casually, A-line skirts balance hips.",
            'formal': "V-neck elongates neck for pears, bold top patterns emphasize upper. Yellow pops on dark. Silk elegant formally.",
            'party': "Fit-and-flare cinches waist and flares over hips for pears. Bright pink contrasts dark. Chiffon flows for parties."
        },
        'mid-dark': {
            'casual': "Off-shoulder broadens shoulders for pear balance, horizontal patterns help. Red warms mid-dark. Linen casual breath.",
            'formal': "V-neck focuses upward for pears. Cream soft on mid-dark. Satin formal sheen.",
            'party': "Fit-and-flare flatters pear curves. Orange energizes mid-dark. Velvet rich for parties."
        },
        'mid-light': {
            'casual': "Off-shoulder adds upper width for pears, horizontal stripes aid. Blue cools mid-light. Cotton casual.",
            'formal': "V-neck draws attention up for pears. Green fresh on mid-light. Wool formal structure.",
            'party': "Fit-and-flare balances pear hips. Lavender calms mid-light. Chiffon party airiness."
        },
        'light': {
            'casual': "Off-shoulder enhances top for pears. Black deepens light. Denim casual tough.",
            'formal': "V-neck elongates for pears. Navy grounds light. Silk formal drape.",
            'party': "Fit-and-flare skims pears gracefully. Maroon enriches light. Sequin party shine."
        }
    },
    'rectangle': {
        'dark': {
            'casual': "Peplum adds waist curve for rectangles, bold prints create illusion. White contrasts dark. Cotton casual comfort.",
            'formal': "Belted defines waist in rectangles, horizontal stripes add width. Yellow bright on dark. Silk formal luxury.",
            'party': "Ruffled creates volume for rectangles. Bright pink pops dark. Chiffon flows, floral adds femininity."
        },
        'mid-dark': {
            'casual': "Peplum flares at hips for rectangle curves. Red warms mid-dark. Linen casual.",
            'formal': "Belted cinches rectangles. Cream elegant mid-dark. Satin formal.",
            'party': "Ruffled adds dimension to rectangles. Orange vibrant mid-dark. Velvet party, polka dots fun."
        },
        'mid-light': {
            'casual': "Peplum creates shape for rectangles. Blue cools mid-light. Cotton casual.",
            'formal': "Belted defines rectangles. Green fresh mid-light. Wool formal.",
            'party': "Ruffled enhances rectangles. Lavender soothes mid-light. Chiffon party, floral romantic."
        },
        'light': {
            'casual': "Peplum adds curves to rectangles. Black contrasts light. Denim casual.",
            'formal': "Belted shapes rectangles. Navy sophisticated light. Silk formal.",
            'party': "Ruffled volumizes rectangles. Maroon deep light. Sequin party, leopard bold."
        }
    }
};

// Auth Routes
app.post("/api/auth/signup", async (req, res) => {
  try {
    const { email, password, name } = req.body;
    const existingUser = await User.findOne({ email });
    if (existingUser) return res.status(400).json({ message: "User already exists" });

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({ email, password: hashedPassword, name });
    await user.save();

    const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET || "secret", { expiresIn: "7d" });
    res.status(201).json({ token, user: { email: user.email, name: user.name } });
  } catch (error) {
    res.status(500).json({ message: "Error creating user" });
  }
});

app.post("/api/auth/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ message: "Invalid credentials" });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ message: "Invalid credentials" });

    const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET || "secret", { expiresIn: "7d" });
    res.json({ token, user: { email: user.email, name: user.name } });
  } catch (error) {
    res.status(500).json({ message: "Error logging in" });
  }
});

// Recommendation Route
app.post("/api/recommend", async (req, res) => {
  try {
    const { bodyShape, skinTone, category } = req.body;
    
    // In a real app, we'd process images here. 
    // For this demo, we use the provided logic based on selected/detected traits.
    const outfit = recommendations[bodyShape]?.[skinTone]?.[category];
    const explanation = explanations[bodyShape]?.[skinTone]?.[category];

    if (!outfit) {
      return res.status(400).json({ message: "No recommendation found for these parameters" });
    }

    res.json({
      bodyShape,
      skinTone,
      category,
      outfit,
      explanation
    });
  } catch (error) {
    res.status(500).json({ message: "Error generating recommendation" });
  }
});

// Vite Middleware for Frontend
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, "dist")));
    app.get("*", (req, res) => {
      res.sendFile(path.join(__dirname, "dist", "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
