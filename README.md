# appnz-rembg

[![Deploy to app.nz](https://app.nz/deploy-button.svg)](https://app.nz/deploy?image=ghcr.io/lee101/appnz-rembg:latest&name=background-remover&hardware=gpu-t4)

A small, production-oriented [Cog](https://github.com/replicate/cog) wrapper
around [rembg](https://github.com/danielgatis/rembg). It removes an image
background and returns a transparent PNG. The default `isnet-general-use`
session is baked into the image and kept warm; alternate models load once and
are reused.

## Run locally

Install Docker and Cog, then:

```bash
cog run -i image=@portrait.jpg -i model=isnet-general-use -o cutout.png
```

Build and serve the exact HTTP image on your own machine:

```bash
cog build -t appnz-rembg
docker run --rm -p 5000:5000 appnz-rembg
curl -s http://localhost:5000/health-check
```

The container implements Cog's `POST /predictions` contract on port 5000 and
also runs on any compatible container host; app.nz is optional.

## Deploy the Cog and its subdomain app

```bash
app cogs deploy background-remover
app apps deploy demo --app rembg-demo
app apps open rembg-demo
```

The first command registers the scale-to-zero model. The demo is a dependency-
free static app served at `https://rembg-demo.app.nz`; enter the deployed Cog id
in its form. Change the `name` in `demo/appnz.yaml` to claim a different
subdomain.

## Test

```bash
python -m unittest discover -s tests -v
python -m json.tool appnz.schema.json >/dev/null
```

The adapter is MIT licensed. rembg is MIT; model weights have their own source
terms and are not redistributed here. See [THIRD_PARTY.md](THIRD_PARTY.md).
