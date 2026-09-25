import os
import threading
import duckdb
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# ------------------------------------------------------------------
# App + DuckDB initialization
# ------------------------------------------------------------------
app = FastAPI(title="Hitek Data Gateway", version="1.2.0")

_db_lock = threading.Lock()
con = duckdb.connect(database=":memory:")
con.execute("LOAD httpfs;")
con.execute("SET threads=2;")
con.execute("SET memory_limit='400MB';")

# ---- Hugging Face authentication ----
# Buckets are public, but we still load the token if provided.
# Useful if you later switch the bucket to private.
HF_TOKEN = "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"
if HF_TOKEN:
    try:
        con.execute(
            f"CREATE OR REPLACE SECRET hf_token "
            f"(TYPE HUGGINGFACE, TOKEN '{HF_TOKEN}');"
        )
        print("[INIT] Hugging Face secret loaded.")
    except Exception as e:
        print(f"[INIT][ERROR] Failed to create HF secret: {e}")
else:
    print("[INIT] No HF_TOKEN set — using anonymous access (fine for public buckets).")


# ------------------------------------------------------------------
# Landing page HTML
# ------------------------------------------------------------------
LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hitek Data Gateway - LIVE</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #050505; color: #00ffcc; font-family: 'Courier New', Courier, monospace; }
        #canvas-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
        .overlay {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            text-align: center; background: rgba(10, 10, 10, 0.85); padding: 50px;
            border: 1px solid #00ffcc; border-radius: 12px; box-shadow: 0 0 30px rgba(0, 255, 204, 0.3);
            backdrop-filter: blur(5px);
        }
        h1 { margin: 0 0 15px 0; font-size: 3.5em; text-transform: uppercase; letter-spacing: 6px; text-shadow: 0 0 15px #00ffcc; }
        p { font-size: 1.2em; margin: 8px 0; color: #ccc; }
        .highlight { color: #00ffcc; font-weight: bold; }
        .status-box {
            margin-top: 30px; font-weight: bold; padding: 15px;
            border-radius: 8px; background: rgba(0, 255, 204, 0.1);
            border: 1px solid rgba(0, 255, 204, 0.5);
            font-size: 1.1em;
        }
        .blinking { animation: blinker 1.5s linear infinite; display: inline-block; }
        @keyframes blinker { 50% { opacity: 0; } }
        .credit { margin-top: 20px; font-size: 0.85em; color: #666; letter-spacing: 2px; }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div class="overlay">
        <h1>SYSTEM ONLINE</h1>
        <p>API Gateway is <span class="highlight">Active &amp; Secured</span></p>
        <p>Parquet Cloud Engine: <span class="highlight">Connected</span></p>
        <div class="status-box">
            <span class="blinking" style="color: #00ffcc;">&#9679;</span> HTTP 200 OK - LISTENING FOR QUERIES
        </div>
        <div class="credit">POWERED BY @ObscuraApis</div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        for (let i = 0; i < 8000; i++) {
            vertices.push(THREE.MathUtils.randFloatSpread(3000));
            vertices.push(THREE.MathUtils.randFloatSpread(3000));
            vertices.push(THREE.MathUtils.randFloatSpread(3000));
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        const material = new THREE.PointsMaterial({ color: 0x00ffcc, size: 2.5, transparent: true, opacity: 0.8 });
        const points = new THREE.Points(geometry, material);
        scene.add(points);

        camera.position.z = 1200;

        function animate() {
            requestAnimationFrame(animate);
            points.rotation.x += 0.0005;
            points.rotation.y += 0.001;
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""


# ------------------------------------------------------------------
# Exception handlers
# ------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "status": "rejected",
                "message": "Invalid endpoint. STRICTLY use /FetchData?Number=XXXXXXXXXX",
                "Developer": "@ObscuraApis"
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "Developer": "@ObscuraApis"}
    )


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def root_landing_page():
    return HTMLResponse(content=LANDING_PAGE_HTML, status_code=200)


@app.get("/health")
def health():
    """Health check endpoint used by Render."""
    return {
        "status": "ok",
        "hf_token_loaded": bool(HF_TOKEN),
        "Developer": "@ObscuraApis"
    }


@app.get("/FetchData")
def fetch_data(Number: str = Query(None)):
    if not Number or not Number.isdigit() or len(Number) < 10 or len(Number) > 15:
        return JSONResponse(
            status_code=400,
            content={
                "status": "rejected",
                "message": "Invalid parameter. STRICTLY use /FetchData?Number=XXXXXXXXXX",
                "Developer": "@ObscuraApis"
            }
        )

    last_digit = Number[-1]

    # ---- FIXED: buckets URL (Xet storage), no /main/ segment ----
    primary_url = (
        f"https://huggingface.co/buckets/CutehackX/hitek-data-bucket/"
        f"tree/final_master_shard_{last_digit}.parquet"
    )
    alt_url = (
        f"https://huggingface.co/buckets/CutehackX/hitek-data-bucket/"
        f"tree/final_master_shard_{last_digit}.parquet"
    )

    try:
        query = f"""
            SELECT *, 'Main' AS _record_type
            FROM read_parquet('{primary_url}')
            WHERE mobile = '{Number}'
            UNION ALL
            SELECT *, 'Alt' AS _record_type
            FROM read_parquet('{alt_url}')
            WHERE alt = '{Number}'
        """

        # DuckDB connection is not thread-safe for concurrent execution
        with _db_lock:
            raw_results = con.execute(query).df().to_dict(orient="records")

        main_records = []
        alt_records = []

        for row in raw_results:
            rec_type = row.pop('_record_type')
            if rec_type == 'Main':
                main_records.append(row)
            else:
                alt_records.append(row)

        if not main_records and not alt_records:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "not_found",
                    "phone": Number,
                    "Developer": "@ObscuraApis"
                }
            )

        return {
            "status": "success",
            "Data": {
                "Main_Records": main_records,
                "Alt_Records": alt_records
            },
            "Developer": "@ObscuraApis"
        }

    except Exception as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err:
            return JSONResponse(
                status_code=502,
                content={
                    "status": "error",
                    "message": (
                        "Hugging Face rejected the request (401). "
                        "The bucket may be private — set HF_TOKEN on Render, "
                        "or confirm the bucket is public."
                    ),
                    "Developer": "@ObscuraApis"
                }
            )
        if "404" in err or "not found" in err.lower():
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": (
                        "Shard file not found on Hugging Face. "
                        "Verify the filename and bucket path are correct."
                    ),
                    "Developer": "@ObscuraApis"
                }
            )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Database processing error: {err}",
                "Developer": "@ObscuraApis"
            }
        )
