use std::fs::File;
use std::io::{BufRead, BufReader};
use std::collections::HashMap;
use std::cmp::max;

fn main() {
    let file = File::open("data/g4.in").expect("Cannot open file");
    let reader = BufReader::new(file);
    let mut lines = reader.lines();
    let (_size, mut graph) = parse_graph(&mut lines);

    println!("Result: {}", algo_r0(&mut graph));
}

fn print_graph(graph: &HashMap<i32, Vec<i32>>) {
    println!("Graph:");
    for (k, v) in graph.iter() {
        println!("{}: {:?}", k, v);
    }
    println!();
}

fn parse_graph(lines: &mut std::io::Lines<BufReader<File>>) -> (i32, HashMap<i32, Vec<i32>>) {
    let size: i32 = lines.next().unwrap().unwrap().parse().unwrap();
    let graph: HashMap<i32, Vec<i32>> = lines
        .map(|line_result| {
            let line = line_result.unwrap();
            line.split_whitespace()
                .enumerate()
                .filter_map(|(i, s)| match s {
                    "1" => Some(i as i32),
                    _ => None
                })
                .collect()
        })
        .enumerate()
        .map(|(i, neighbours)| (i as i32, neighbours))
        .collect();
    (size, graph)
}

fn remove_vertex(graph: &mut HashMap<i32, Vec<i32>>, vertex: &i32) {
    graph.remove(vertex);

    for adjacency_list in graph.values_mut() {
        adjacency_list.retain(|v| v != vertex);
    }
}

fn find_priority_node(graph: &HashMap<i32, Vec<i32>>) -> (Option<i32>, Option<i32>, Option<i32>) {
    let mut node_with_one_neighbour: Option<i32> = None;
    let mut node_with_maximum_neighbours: Option<i32> = None;

    for (node, neighbours) in graph.iter() {
        match neighbours.len() {
            0 => return (Some(*node), None, None),
            1 => node_with_one_neighbour = Some(*node),
            v => {
                if node_with_maximum_neighbours.is_none() || v > node_with_maximum_neighbours.unwrap() as usize {
                    node_with_maximum_neighbours = Some(*node);
                }
            }
        }
    }
    (None, node_with_one_neighbour, node_with_maximum_neighbours)
}

fn algo_r0(graph: &mut HashMap<i32, Vec<i32>>) -> i32 {
    if graph.is_empty() {
        return 0;
    }

    let priority_nodes = find_priority_node(graph);

    if let (Some(isolated), None, None) = priority_nodes {
        let mut graph_copy = graph.clone();
        remove_vertex(&mut graph_copy, &isolated);
        return 1 + algo_r0(&mut graph_copy);
    } else if let (_, _, Some(maximum)) = priority_nodes {
        let mut graph_one = graph.clone();
        let mut graph_two = graph.clone();

        remove_vertex(&mut graph_one, &maximum);

        for neighbour in graph.get(&maximum).unwrap().iter() {
            remove_vertex(&mut graph_two, neighbour);
        }

        return max(algo_r0(&mut graph_one), 1 + algo_r0(&mut graph_two));
    } else {
        println!("Error: No priority nodes found");
        return -1;
    }
}

