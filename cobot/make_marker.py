"""Gera um marcador ArUco para impressao (cole na peca para os testes reais).

Uso:
    python make_marker.py            # marcador id 0, dict DICT_4X4_50
    python make_marker.py --id 0 --size 600
"""
import argparse
import cv2


def main():
    p = argparse.ArgumentParser(description="Gera marcador ArUco para impressao")
    p.add_argument("--id", type=int, default=0, help="ID do marcador")
    p.add_argument("--dict", default="DICT_4X4_50", help="Dicionario ArUco")
    p.add_argument("--size", type=int, default=600, help="Tamanho em px")
    p.add_argument("--out", default=None, help="Arquivo de saida")
    args = p.parse_args()

    aruco = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, args.dict))
    img = cv2.aruco.generateImageMarker(aruco, args.id, args.size)
    out = args.out or f"marker_{args.dict}_id{args.id}.png"
    cv2.imwrite(out, img)
    print(f"Marcador salvo em: {out}")
    print("Imprima, cole na peca e ajuste target_marker_id em vision/config.py se mudar o ID.")


if __name__ == "__main__":
    main()
