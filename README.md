# Arctic Arc Layer

An interactive pydeck visualization of connections between Arctic research and logistics hubs. It is based on the [deck.gl Arc Layer example](https://deck.gl/examples/arc-layer) and its [pydeck implementation](https://github.com/visgl/deck.gl/blob/master/bindings/pydeck/examples/arc_layer.py).

## Run

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv run main.py
```

This creates `arctic_globe_view.html`. It uses pydeck's experimental `_GlobeView` with a filled country layer, Arctic routes, and hub markers. Open the file in a browser to explore the globe, hover over arcs for route details, and drag the globe to inspect the connections.

## GitHub Actions

Every push to `main` builds the HTML with `uv` and uploads it as the `arctic-globe-view` artifact. Open the repository's **Actions** tab, select a successful **Build visualization** run, and download the artifact from the **Artifacts** section.