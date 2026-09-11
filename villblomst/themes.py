"""Temadefinisjoner og nøkkelordmatching (port av Themes.swift)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .scraper import decode_html

_TOKEN_RE = re.compile(r"[^0-9a-zA-ZæøåÆØÅäöüÄÖÜ]+")


@dataclass(frozen=True)
class WallpaperTheme:
    id: str
    name: str
    icon: str
    keywords: tuple[str, ...] = field(default_factory=tuple)

    def matches(self, title: str) -> bool:
        if not self.keywords:
            return True
        cleaned = decode_html(title).lower()
        tokens = set(_TOKEN_RE.split(cleaned))
        for keyword in self.keywords:
            if " " in keyword:
                if keyword in cleaned:
                    return True
            elif keyword in tokens:
                return True
        return False


THEMES: list[WallpaperTheme] = [
    WallpaperTheme("alle", "Alle", "grid", ()),
    WallpaperTheme(
        "blomster",
        "Blomster",
        "flower",
        (
            "flower", "flowers", "wildflower", "wildflowers", "blossom", "blossoms",
            "bloom", "blooms", "blooming", "flowering", "meadow", "meadows",
            "garden", "gardens", "botanical", "botanic", "tulip", "tulips",
            "rose", "roses", "orchid", "orchids", "daisy", "poppy", "poppies",
            "lavender", "sunflower", "sunflowers", "lilies", "lily", "iris",
            "fern", "ferns", "petal", "petals", "flora", "cactus", "succulent",
            "clover", "bluebell", "bluebells", "foxglove", "thistle", "dandelion",
            "magnolia", "hibiscus", "anemone", "anemones", "hydrangea", "peony",
            "peonies", "jasmine", "azalea", "azaleas", "rhododendron",
            "rhododendrons", "wisteria", "lupine", "lupines", "lupin", "lotus",
            "violet", "violets", "pansy", "geranium", "begonia", "camellia",
            "coneflower", "cornflower", "snapdragon", "marigold", "verbena",
            "chicory", "buttercup", "primrose", "gentian", "fireweed", "heather",
            "crocus", "crocuses", "hyacinth", "hyacinths", "dahlia", "protea",
            "trillium", "balsamroot", "phlox", "narcissus", "daffodil",
            "daffodils", "allium", "fuchsia", "water lily", "water lilies",
        ),
    ),
    WallpaperTheme(
        "natur",
        "Natur",
        "tree",
        (
            "forest", "forests", "tree", "trees", "woodland", "rainforest",
            "jungle", "mountain", "mountains", "valley", "canyon", "canyons",
            "glacier", "glaciers", "volcano", "waterfall", "waterfalls", "river",
            "lake", "lakes", "meadow", "meadows", "wilderness", "cliff", "cliffs",
            "hill", "hills", "grassland", "savanna", "steppe", "prairie",
            "tundra", "swamp", "marsh", "geyser", "cave", "caves", "pine", "pines",
            "sequoia", "redwood", "bamboo", "autumn", "blooming", "coral",
            "reef", "lagoon", "fjord", "badlands", "desert", "dunes",
        ),
    ),
    WallpaperTheme(
        "dyr",
        "Dyr",
        "paw",
        (
            "bear", "bears", "fox", "foxes", "wolf", "wolves", "deer", "elk",
            "moose", "reindeer", "bird", "birds", "eagle", "owl", "owls",
            "butterfly", "butterflies", "bee", "bees", "whale", "whales", "shark",
            "sharks", "dolphin", "dolphins", "seal", "seals", "penguin",
            "penguins", "elephant", "elephants", "lion", "lions", "tiger",
            "tigers", "leopard", "cheetah", "monkey", "monkeys", "giraffe",
            "giraffes", "zebra", "zebras", "turtle", "turtles", "frog", "frogs",
            "lizard", "snake", "snakes", "squirrel", "rabbit", "rabbits", "hare",
            "horse", "horses", "cattle", "sheep", "goat", "cats", "dogs", "crab",
            "octopus", "fish", "fishes", "hummingbird", "flamingo", "crane",
            "swan", "duck", "geese", "parrot", "toucan", "puffin", "heron",
            "kingfisher", "rhino", "hippopotamus", "bison", "camel", "llama",
            "alpaca", "kangaroo", "koala", "panda", "orangutan", "lemur",
            "walrus", "manatee", "macaw", "macaws", "toucan", "owlet", "lions",
        ),
    ),
    WallpaperTheme(
        "by",
        "By",
        "city",
        (
            "city", "cityscape", "skyline", "building", "buildings", "architecture",
            "street", "streets", "town", "village", "bridge", "bridges", "harbor",
            "harbour", "downtown", "skyscraper", "skyscrapers", "temple", "tower",
            "towers", "castle", "church", "cathedral", "mosque", "palace",
            "market", "alley", "avenue", "metro", "subway", "cafe", "boulevard",
            "waterfront", "district", "rooftops", "urban", "village", "homes",
            "boats", "canal",
        ),
    ),
    WallpaperTheme(
        "landskap",
        "Landskap",
        "mountain",
        (
            "landscape", "desert", "canyon", "valley", "valleys", "hills",
            "plateau", "mesa", "coast", "coastline", "dunes", "field", "fields",
            "farmland", "terrace", "terraces", "sunrise", "sunset", "horizon",
            "badlands", "fjord", "glacier", "mountains", "mountain", "cliffs",
            "cliff", "prairie", "savanna", "valley", "river", "lake",
        ),
    ),
    WallpaperTheme(
        "hav",
        "Hav og vann",
        "waves",
        (
            "ocean", "sea", "beach", "beaches", "coast", "coastline", "island",
            "islands", "lagoon", "reef", "coral", "underwater", "bay", "gulf",
            "harbor", "harbour", "waves", "tide", "shore", "shoreline", "pier",
            "lighthouse", "boat", "boats", "ship", "sailboat", "kayak", "surf",
            "lake", "river", "waterfall", "waterfalls", "water", "iceberg",
        ),
    ),
    WallpaperTheme(
        "verdensrom",
        "Verdensrom",
        "moon",
        (
            "space", "galaxy", "galaxies", "milky way", "aurora", "auroras",
            "northern lights", "stars", "starry", "nebula", "moon", "planet",
            "planets", "saturn", "jupiter", "mars", "comet", "meteor", "eclipse",
            "observatory", "telescope", "nasa", "astronaut", "star trails",
            "night sky",
        ),
    ),
    WallpaperTheme(
        "host",
        "Høst og vinter",
        "snow",
        (
            "autumn", "fall", "winter", "snow", "snowy", "frost", "frosty",
            "ice", "frozen", "hoarfrost", "maple", "leaves", "pumpkin",
            "christmas", "holiday", "holidays", "mistletoe", "pine", "pinecone",
        ),
    ),
]


def theme_by_id(theme_id: str) -> WallpaperTheme:
    return next((t for t in THEMES if t.id == theme_id), THEMES[0])
