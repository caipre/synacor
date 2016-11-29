fn main() {
    for reg7 in 0..32767 {
        let mut stck = vec![];
        let mut reg0 = 4;
        let mut reg1 = 1;
        let mut cntr = 0;
        solve(&mut cntr, &mut reg0, &mut reg1, reg7, &mut stck);
        if reg0 == 6 {
            println!("\r{} {} {}", reg7, reg0, reg1);
        }
    }
}

fn solve(cntr: &mut isize, reg0: &mut isize, reg1: &mut isize, reg7: isize, stck: &mut Vec<isize>) {
    if *cntr == -1 || *cntr > 100_000_000 {
        *cntr = -1;
        return
    }
    *cntr += 1;

    if *reg0 == 0 {
        *reg0 = (*reg1 + 1) % 32768;
    }
    else if *reg1 == 0 {
        *reg0 -= 1;
        *reg1 = reg7;
        solve(cntr, reg0, reg1, reg7, stck);
    }
    else {
        stck.push(*reg0);
        *reg1 -= 1;
        solve(cntr, reg0, reg1, reg7, stck);
        *reg1 = *reg0;
        *reg0 = stck.pop().unwrap();
        *reg0 -= 1;
        solve(cntr, reg0, reg1, reg7, stck);
    }
}
