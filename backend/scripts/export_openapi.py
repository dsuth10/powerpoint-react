import argparse
import json
from app.main import app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, required=True)
    args = parser.parse_args()

    # FastAPI app has custom_openapi assigned; app.openapi() returns dict
    schema = app.openapi()
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(schema, f)


if __name__ == '__main__':
    main()


