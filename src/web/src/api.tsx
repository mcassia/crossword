 
export interface Clue {
    row: number;
    column: number;
    word: string;
    definitions: string[];
    length: number;
    direction: Direction;
    index: number;
}

export enum Direction {
    Horizontal,
    Vertical,
}

interface Template {
    rows: (boolean|number)[];
}

// interface HttpResponse<T> extends Response {
//     parsedBody?: T;
//   }

export async function http<T>(
    request: RequestInfo
): Promise<Response> {
    const response: Response = await fetch(request);
    return response;
}

export async function post<T>(
    path: string,
    body: any,
    args: RequestInit = { method: "post", body: JSON.stringify(body) }
  ): Promise<Response>  {
    return await http<T>(new Request(path, args));
  };
  
  
export const getCluesAndBoard = async (template: (number|boolean)[][]): Promise<{completed: boolean, clues: Clue[], board: string[][]}> => {
    const response = await post< {completed: boolean, clues: Clue[], board: string[][]} >(
        "http://localhost:8890/",
        template
    );
    return response.json()
}