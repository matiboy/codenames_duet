export interface Player {
  attempted_words: string[];
  loaded: boolean;
  name: string;
}

export interface Attendee {
  AttendeeId: string;
  ExternalUserId: string;
  JoinToken: string;
}

export interface Game {
    agents: number;
    bystanders: number;
    found: string[];
    id: string;
    initialBystanders: number;
    keys: number;
    next_up: number;
    player1: Player;
    player2: Player;
    words: string[];
}