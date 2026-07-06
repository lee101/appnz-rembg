# appnz-rembg

[![Deploy to app.nz](https://app.nz/deploy-button.svg)](https://app.nz/deploy?image=ghcr.io/lee101/appnz-rembg:latest&name=rembg&hardware=auto)

Background removal with [rembg](https://github.com/danielgatis/rembg)
(isnet-general-use by default) packaged as an [app.nz cog](https://app.nz):
a tiny HTTP contract on port 5000 with `POST /predictions` in and a
transparent PNG data URI out. CPU onnxruntime — small, fast, no GPU needed.
The default model is baked into the image for fast cold starts; other models
download on first use.

## Inputs

| name | type | notes |
|---|---|---|
| `image` | image | https URL or `data:` URI |
| `model` | enum | `isnet-general-use` (default), `u2net`, `u2netp`, `isnet-anime`, `birefnet-general` |

Output: `data:image/png;base64,...` with transparent background.

## Run locally

```bash
docker run -p 5000:5000 ghcr.io/lee101/appnz-rembg:latest

curl -s http://localhost:5000/health-check

curl -s http://localhost:5000/predictions -X POST \
  -H 'Content-Type: application/json' \
  -d '{"input": {"image": "https://example.com/photo.jpg"}}' \
  | python3 -c 'import sys,json,base64; open("out.png","wb").write(base64.b64decode(json.load(sys.stdin)["output"].split(",",1)[1]))'
```

## One-click deploy on app.nz

Click the badge above, or open
`https://app.nz/deploy?image=ghcr.io/lee101/appnz-rembg:latest&name=rembg&hardware=auto`.

## Build

```bash
docker build -t ghcr.io/lee101/appnz-rembg:latest .
```

GitHub Actions builds and pushes `ghcr.io/lee101/appnz-rembg:latest` on every
push to `main`.

## License

MIT
