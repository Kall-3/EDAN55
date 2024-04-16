use std::fs::File;
use std::io::{BufRead, BufReader};
use rand::Rng;
use std::vec::Vec;
use std::collections::HashSet;
use std::time::Instant;


fn main() {
    let file = File::open("data/matching_1000.txt").expect("Cannot open file");
    // let file = File::open("data/pw09_100.9.txt").expect("Cannot open file");
    let reader = BufReader::new(file);

    let mut lines = reader.lines();

    let first_line = lines.next().unwrap().unwrap().split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect::<Vec<i32>>();
    let edges: Vec<Vec<i32>> = lines
        .map(|line_result| {
            let line = line_result.unwrap();
            line.split_whitespace()
                .map(|s| s.parse().unwrap())
                .collect()
        }).collect();

    let nodes = first_line[0];
    let weights = first_line[1];
    println!("Nodes: {}, Weights: {}", nodes, weights);

    let itterations = 5;

    let mut tot_cut = 0;
    let mut highest_cut = 0;
    let start_r = Instant::now();
    for _ in 0..itterations {
        let (graph_a, graph_b) = init_r(nodes);
        let cut = cut(&graph_a, &graph_b, &edges);
        tot_cut += cut;
        highest_cut = highest_cut.max(cut);
    }
    let elapsed_r = start_r.elapsed();
    println!("Highest R maxcut: {:?}", highest_cut);
    println!("Average R maxcut: {:?}", tot_cut / itterations);
    println!("Time: {:?}", elapsed_r);

    let mut tot_cut = 0;
    let mut highest_cut = 0;
    let start_s = Instant::now();
    for _ in 0..itterations {
        let cut = maxcut_s(nodes, HashSet::<i32>::new(), (1..=nodes).collect::<HashSet<i32>>(), &edges);
        tot_cut += cut;
        highest_cut = highest_cut.max(cut);
    }
    let elapsed_s = start_s.elapsed();
    println!("Highest S maxcut: {:?}", highest_cut);
    println!("Average S maxcut: {:?}", tot_cut / itterations);
    println!("Time: {:?}", elapsed_s);


    let mut tot_cut = 0;
    let mut highest_cut = 0;
    let start_rs = Instant::now();
    for _ in 0..itterations {
        let (graph_a, graph_b) = init_r(nodes);
        let cut = maxcut_s(nodes, graph_a, graph_b, &edges);
        tot_cut += cut;
        highest_cut = highest_cut.max(cut);
    }
    let elapsed_rs = start_rs.elapsed();
    println!("Highest RS maxcut: {:?}", highest_cut);
    println!("Average RS maxcut: {:?}", tot_cut / itterations);
    println!("Time: {:?}", elapsed_rs);
}

fn init_r(nodes: i32) -> (HashSet<i32>, HashSet<i32>) {
    let mut rng = rand::thread_rng();
    let mut graph_a = HashSet::new();
    let mut graph_b = HashSet::new();

    for i in 1..=nodes {
        if rng.gen() {
            graph_a.insert(i);
        } else {
            graph_b.insert(i);
        }
    }
    (graph_a, graph_b)
}


fn maxcut_s(nodes: i32, mut graph_a: HashSet<i32>, mut graph_b: HashSet<i32>, edges: &Vec<Vec<i32>>) -> i32 {
    let mut prev_cut = -1;
    let mut best_cut = cut(&graph_a, &graph_b, edges);

    while best_cut > prev_cut {
        prev_cut = best_cut;
        for i in 0..nodes {
            if graph_a.contains(&i) {
                graph_a.remove(&i);
                graph_b.insert(i);
                let cut = cut(&graph_a, &graph_b, edges);
                if cut > best_cut {
                    best_cut = cut;
                } else {
                    graph_a.insert(i);
                    graph_b.remove(&i);
                }
            }
            if graph_b.contains(&i) {
                graph_a.insert(i);
                graph_b.remove(&i);
                let cut = cut(&graph_a, &graph_b, edges);
                if cut > best_cut {
                    best_cut = cut;
                } else {
                    graph_a.remove(&i);
                    graph_b.insert(i);
                }
            }
        }
    }
    best_cut
}

fn cut(graph_a: &HashSet<i32>, graph_b: &HashSet<i32>, edges: &Vec<Vec<i32>>) -> i32 {
    edges.iter().filter(|edge| {
        (graph_a.contains(&edge[0]) && graph_b.contains(&edge[1])) ||
        (graph_b.contains(&edge[0]) && graph_a.contains(&edge[1]))
    }).map(|edge| edge[2]).sum()
}
