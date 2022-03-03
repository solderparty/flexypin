import argparse
import os


def s_expr(indent, *args, **kwargs):
    def fix(args):
        args = list(args)

        for i, arg in enumerate(args):
            if type(arg) == float:
                args[i] = '{:.2f}'.format(arg)
            else:
                args[i] = str(arg)

        return args

    s = ' '.join(fix(args))

    args = []
    for k, v in kwargs.items():
        if type(v) == list:
            args.append(s_expr(0, k, ' '.join(fix(v))))
        else:
            args.append(s_expr(0, k, v))

    if args:
        s += ' '

    s += ' '.join(args)

    return indent * ' ' + '(' + s + ')'


def generate(output, pitch, num):
    name = 'FlexyPin_1x{:02d}_P{:.2f}mm'.format(num, pitch)
    path = '{}/{}.kicad_mod'.format(output, name)
    
    s = s_expr(0, 'module', name, layer='F.Cu')[:-1] + '\n'

    # Labels
    s += s_expr(2, 'fp_text', 'reference', 'REF**', at=[0, -1.25], layer='F.SilkS', effects=s_expr(0, 'font', size=[1, 1], thickness=0.15)) + '\n'
    s += s_expr(2, 'fp_text', 'value', name, at=[0, pitch * (num - 1) + 1.3], layer='F.Fab', effects=s_expr(0, 'font', size=[1, 1], thickness=0.15)) + '\n'
    s += '\n'

    # Courtyard
    s += s_expr(2, 'fp_line', start=[-1.1, pitch * (num - 1) + 0.6], end=[-1.1,                    -0.6], layer='F.CrtYd', width=0.1) + '\n'
    s += s_expr(2, 'fp_line', start=[ 2.7, pitch * (num - 1) + 0.6], end=[-1.1, pitch * (num - 1) + 0.6], layer='F.CrtYd', width=0.1) + '\n'
    s += s_expr(2, 'fp_line', start=[ 2.7,                    -0.6], end=[ 2.7, pitch * (num - 1) + 0.6], layer='F.CrtYd', width=0.1) + '\n'
    s += s_expr(2, 'fp_line', start=[-1.1,                    -0.6], end=[ 2.7,                    -0.6], layer='F.CrtYd', width=0.1) + '\n'
    s += '\n'

    # Pads
    for i in range(num):
        s += s_expr(2, 'pad', i + 1, 'thru_hole', 'rect', at=[0,    i * pitch], size=[1.3, 0.90], drill=[0.6, s_expr(0, 'offset', -0.3, 0)], layers=['*.Cu', '*.Mask']) + '\n'
        s += s_expr(2, 'pad', '""',  'thru_hole', 'oval', at=[1.55, i * pitch], size=[2.0, 0.95], drill=['oval', 1.7, 0.65],                 layers=['*.Cu', '*.Mask']) + '\n'
        s += s_expr(2, 'model', '${KIPRJMOD}/../3d/flexypin.step', offset=s_expr(0, 'xyz', 0, -i * pitch, 0), scale=s_expr(0, 'xyz', 1, 1, 1), rotate=s_expr(0, 'xyz', 0, 0, 0)) + '\n'
        s += '\n'

    s += ')'

    mod = open(path, 'w')
    mod.write(s)
    mod.close()

    #print(s)
    print(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate FlexyPin footprints', usage='%(prog)s [options]')
    parser.add_argument('-o', '--output', type=str, default='./output', help='output path (default: %(default)s)')
    parser.add_argument('-p', '--pitch', type=float, default=2.54, help='pin pitch (default: %(default)s)')
    parser.add_argument('-n', '--num', type=int, default=1, help='pin number (default: %(default)s)')
    parser.add_argument('-r', '--range', help='generate from 1 to [num] instead of just [num]', action='store_true')
    
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.range:
        for i in range(1, args.num + 1):
            generate(args.output, args.pitch, i)
    else:
        generate(args.output, args.pitch, args.num)
